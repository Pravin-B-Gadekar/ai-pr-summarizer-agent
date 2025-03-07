import os
import base64
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import google.generativeai as genai
from github import Github, GithubIntegration

# Load environment variables from .env file
load_dotenv()


class PRReviewBot:
    def __init__(self):
        # GitHub App credentials
        self.app_id = os.getenv("GITHUB_APP_ID")
        self.private_key = os.getenv("GITHUB_PRIVATE_KEY")
        self.installation_id = os.getenv("GITHUB_INSTALLATION_ID")

        # Gemini API key
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Check for required environment variables
        if not self.app_id or not self.private_key or not self.installation_id:
            raise ValueError(
                f"""Missing required environment variables:
                APP_ID: {bool(self.app_id)}
                PRIVATE_KEY: {bool(self.private_key)}
                INSTALLATION_ID: {bool(self.installation_id)}"""
            )

        if not self.gemini_api_key:
            raise ValueError("Missing GEMINI_API_KEY environment variable.")

        # Initialize Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

        # Initialize GitHub integration
        self.integration = GithubIntegration(
            self.app_id,
            self.private_key
        )

        # Get an access token for the installation
        self.access_token = self.integration.get_access_token(int(self.installation_id)).token
        self.github = Github(self.access_token)

    def get_file_content(self, owner, repo, path, ref):
        """
        Retrieves the content of a file from a GitHub repository at a specific reference.
        """
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            file_content = repository.get_contents(path, ref=ref)
            if isinstance(file_content, list):
                return None  # This is a directory, not a file
            return base64.b64decode(file_content.content).decode('utf-8')
        except Exception as e:
            if "404" in str(e):
                print(f"File {path} not found at ref {ref}")
                return None
            raise e

    def parse_review_xml(self, xml_text):
        """
        Parses XML response from the AI model into a structured format.
        """
        try:
            # Find the review XML section
            xml_start = xml_text.find("<review>")
            xml_end = xml_text.find("</review>") + len("</review>")

            if xml_start == -1 or xml_end == -1:
                print("Could not locate <review> tags in the AI response. Returning fallback.")
                return {
                    "summary": "AI analysis could not parse the response from the model.",
                    "file_analyses": [],
                    "overall_suggestions": []
                }

            # Extract XML portion
            xml_response = xml_text[xml_start:xml_end]

            # Parse XML
            root = ET.fromstring(xml_response)

            # Extract data
            summary = root.find("summary").text.strip() if root.find("summary") is not None else ""

            file_analyses = []
            file_analyses_element = root.find("fileAnalyses")
            if file_analyses_element is not None:
                for file_elem in file_analyses_element.findall("file"):
                    path = file_elem.find("path").text.strip() if file_elem.find("path") is not None else "Unknown file"
                    analysis = file_elem.find("analysis").text.strip() if file_elem.find("analysis") is not None else ""
                    file_analyses.append({"path": path, "analysis": analysis})

            overall_suggestions = []
            suggestions_element = root.find("overallSuggestions")
            if suggestions_element is not None:
                for suggestion_elem in suggestions_element.findall("suggestion"):
                    if suggestion_elem.text:
                        overall_suggestions.append(suggestion_elem.text.strip())

            return {
                "summary": summary,
                "file_analyses": file_analyses,
                "overall_suggestions": overall_suggestions
            }
        except Exception as e:
            print(f"Error parsing AI-generated XML: {e}")
            return {
                "summary": "We were unable to fully parse the AI-provided code analysis.",
                "file_analyses": [],
                "overall_suggestions": []
            }

    def analyze_code(self, title, changed_files, commit_messages):
        """
        Sends code to Gemini for analysis and parses the response.
        """
        # Format commit messages
        commit_message_list = []
        for msg in commit_messages:
            commit_message_list.append(f"- {msg}")
        commit_messages_str = "\n".join(commit_message_list)

        # Format changed files
        changed_files_list = []
        for file in changed_files:
            file_content = file['content'] if file['content'] else 'N/A'
            file_str = f"""
File: {file['filename']}
Status: {file['status']}
Diff:
{file['patch']}

Current Content:
{file_content}
"""
            changed_files_list.append(file_str)
        changed_files_str = "\n---\n".join(changed_files_list)

        # Build prompt for the AI
        prompt = f"""You are an expert code reviewer. Analyze these pull request changes and provide detailed feedback.
Write your analysis in clear, concise paragraphs. Do not use code blocks for regular text.
Format suggestions as single-line bullet points.

Context:
PR Title: {title}
Commit Messages: 
{commit_messages_str}

Changed Files:
{changed_files_str}

Provide your review in the following XML format:
<review>
  <summary>Write a clear, concise paragraph summarizing the changes</summary>
  <fileAnalyses>
    <file>
      <path>file path</path>
      <analysis>Write analysis as regular paragraphs, not code blocks</analysis>
    </file>
  </fileAnalyses>
  <overallSuggestions>
    <suggestion>Write each suggestion as a single line</suggestion>
  </overallSuggestions>
</review>"""

        try:
            # Generate response from Gemini
            response = self.model.generate_content(prompt)

            # Parse the XML response
            return self.parse_review_xml(response.text)
        except Exception as e:
            print(f"Error generating or parsing AI analysis: {e}")
            return {
                "summary": "We were unable to analyze the code due to an internal error.",
                "file_analyses": [],
                "overall_suggestions": []
            }

    def post_placeholder_comment(self, owner, repo, pull_number):
        """
        Posts an initial placeholder comment on the PR.
        """
        repository = self.github.get_repo(f"{owner}/{repo}")
        pr = repository.get_pull(pull_number)
        comment = pr.create_issue_comment("AI code review in progress... Please wait.")
        return comment.id

    def update_comment_with_review(self, owner, repo, comment_id, analysis):
        """
        Updates the placeholder comment with the final review.
        """
        # Format file analyses
        file_analyses_list = []
        for file in analysis['file_analyses']:
            file_analyses_list.append(f"## {file['path']}\n{file['analysis']}")
        file_analyses_str = "\n\n".join(file_analyses_list)

        # Format suggestions
        suggestions_list = []
        for suggestion in analysis['overall_suggestions']:
            suggestions_list.append(f"• {suggestion}")
        suggestions_str = "\n".join(suggestions_list)

        # Format the review as markdown
        final_review_body = f"""# AI Code Review

    {analysis['summary']}

    {file_analyses_str}

    ## Suggestions for Improvement
    {suggestions_str}

    ---
    *Generated by Google Gemini AI Bot*"""

        try:
            # Get the repository
            repository = self.github.get_repo(f"{owner}/{repo}")

            # The correct way to get an issue comment in PyGithub is through the _requester
            headers, data = repository._requester.requestJsonAndCheck(
                "PATCH",
                f"/repos/{owner}/{repo}/issues/comments/{comment_id}",
                input={"body": final_review_body}
            )
            print(f"Successfully updated comment {comment_id}")
        except Exception as e:
            print(f"Error updating comment {comment_id}: {e}")

    def handle_pull_request_opened(self, payload):
        """
        Main handler for 'pull_request opened' event.
        """
        owner = payload["repository"]["owner"]["login"]
        repo = payload["repository"]["name"]
        pull_number = payload["pull_request"]["number"]
        title = payload["pull_request"]["title"]
        head_ref = payload["pull_request"]["head"]["sha"]

        try:
            # Post placeholder comment
            placeholder_comment_id = self.post_placeholder_comment(owner, repo, pull_number)

            # Get repository and PR objects
            repository = self.github.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(pull_number)

            # Get changed files
            files = pr.get_files()
            changed_files = []

            for file in files:
                content = None
                if file.status != "removed":
                    try:
                        content = self.get_file_content(owner, repo, file.filename, head_ref)
                    except Exception as e:
                        print(f"Error retrieving content for {file.filename}: {e}")

                changed_files.append({
                    "filename": file.filename,
                    "patch": file.patch or "",
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "content": content
                })

            # Get commit messages
            commits = pr.get_commits()
            commit_messages = [commit.commit.message for commit in commits]

            # Analyze code
            analysis = self.analyze_code(title, changed_files, commit_messages)

            # Update comment with review
            self.update_comment_with_review(owner, repo, placeholder_comment_id, analysis)

            print(f"Submitted code review for PR #{pull_number} in {owner}/{repo}")
            return True
        except Exception as e:
            print(f"Failed to handle 'pull_request' opened event for PR #{pull_number}: {e}")
            return False


# Initialize Flask app
app = Flask(__name__)
pr_bot = PRReviewBot()


@app.route('/')
def index():
    return "PR Review Bot is running"


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get event type and payload
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json

        # Handle pull request events
        if event_type == "pull_request" and payload.get("action") == "opened":
            # Return a 200 response immediately
            print(f"Received PR opened event, starting processing in background")

            # Start processing in a separate thread to avoid blocking the response
            import threading
            thread = threading.Thread(target=pr_bot.handle_pull_request_opened, args=(payload,))
            thread.daemon = True  # Allow the thread to be terminated when the main program exits
            thread.start()

            return jsonify({"status": "Processing started"}), 200

        return jsonify({"status": "Event received"}), 200
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)