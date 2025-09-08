import uuid

from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.answer import Answer
from vital_llm_reasoner.ensemble.member.ensemble_member import EnsembleMember
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry
from vital_llm_reasoner.ensemble.member.task_tag import TaskTag
import asyncio
# from pyppeteer import launch

# TODO switch to playwright

from black import format_str, FileMode

# this is meant to create a separate browser session
# per request that inits with the request and exits when request completes
# it is meant to expose the virtual file system over the life of the request

# up request init a number of files may be "put" into the file system that
# the reasoner may access.
# functions like "extract_text" may act on these to insert a new file
# with extracted text, which may be implemented by a separate tool or service
# so the reasoner calling extract_text(input file, output file) may end up
# creating a new output file which the reasoner may get via get_file(filename)
# or pass it to the assisting LLM without reading it.

# decide on using directory like /persistent or /home

# code execution to have access to the files in the file system
# code execution can write files into the file system

# include a "reboot" function to reset that would include the
# initial files for the session

# workflow could be to have assistant LLM write code
# write that into the file system
# use code executor to run it
# check results and provide feedback to assistant to re-try if needed

# returning file system content to the caller
# could be added into the final response as a new field

# completing the request could write it into a permanent store tied
# to the request id, such as kgraphservice in s3.

# the reasoner could have ensemble call to "export" particular files
# to specifically store them in kgraphservice

# mechanism to search for files in kgraphservice (vector search)
# and then bring those into the file system for local processing
# could be the way to find relevant source code in a code base

# consider case of writing documentation, such as managed by gitbook in github
# where a set of files would be brought into the file system
# for editing and syncing back to git
# using markdown

# potentially this is more of a virtual file system that can list files
# from git, gdrive, etc. and only some of them are actually in the local in-memory file system at a time.

# potentially have the extern file system like github, gdrive accessible via
# separate ensemble member(s) and then copy files from extern to local and vice versa.

# ensemble tool for querying file system could internally
# use kgraphservice and return paths for files in the file system
# which would allow querying documents in a GitHub repo


class FilesystemMember(EnsembleMember):

    def __init__(self, *, config: ReasonerConfig | None = None):
        super().__init__(config=config)
        self.browser = None
        self.page = None

    @classmethod
    def get_task_tag(cls) -> TaskTag:
        task_tag = TaskTag('code_executor')
        return task_tag

    def handle_inquiry(self, inquiry: Inquiry, context: str = None) -> Answer:
        pass

    async def start(self):
        # self.browser = await launch(headless=True)
        self.page = await self.browser.newPage()
        await self.page.goto(
            'data:text/html,<script src="https://cdn.jsdelivr.net/pyodide/v0.23.0/full/pyodide.js"></script>')
        await self.page.evaluate("""
                async function initializePyodide() {
                    if (!window.pyodide) {
                        window.pyodide = await loadPyodide();
                        // Set up a persistent directory
                        pyodide.runPython(`
    import os
    if not os.path.exists('/persistent'):
        os.makedirs('/persistent')
    `);
                    }
                }
                initializePyodide();
            """)

    async def run_code(self, code_string):
        if not self.browser or not self.page:
            raise RuntimeError("PyodideRunner not started. Call 'start()' first.")

        result = await self.page.evaluate(f"""
                async () => {{
                    try {{
                        // Execute the Python code
                        pyodide.runPython(`{code_string}`);

                        // Retrieve any desired outputs
                        const output = pyodide.runPython(`
    import os
    import sys
    from io import StringIO

    sys.stdout = StringIO()  # Capture stdout for this execution
    exec('''
    {code_string}
    ''')
    stdout_content = sys.stdout.getvalue()
    stdout_content
                        `);

                        return {{ success: true, output }};
                    }} catch (error) {{
                        return {{ success: false, error: error.toString() }};
                    }}
                }}
            """)
        return result

    async def put_file(self, name, content):
        """Put a file in the VFS."""
        if not isinstance(content, bytes):
            raise ValueError("Content must be bytes.")
        encoded_content = content.decode('latin1')  # Use 'latin1' for safe byte encoding
        await self.page.evaluate(f"""
                pyodide.FS.writeFile('/persistent/{name}', atob('{encoded_content}'));
            """)

    async def list_files(self):
        """List all files in the persistent directory."""
        return await self.page.evaluate("""
                pyodide.FS.readdir('/persistent').filter(file => file !== '.' && file !== '..');
            """)

    async def delete_file(self, name):
        """Delete a file from the VFS."""
        return await self.page.evaluate(f"""
                pyodide.FS.unlink('/persistent/{name}');
            """)

    async def get_file(self, name):
        """Retrieve the content of a file."""
        content = await self.page.evaluate(f"""
                pyodide.FS.readFile('/persistent/{name}', {{ encoding: 'binary' }});
            """)
        return content.encode('latin1')  # Decode 'latin1' back to bytes

    async def stop(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
