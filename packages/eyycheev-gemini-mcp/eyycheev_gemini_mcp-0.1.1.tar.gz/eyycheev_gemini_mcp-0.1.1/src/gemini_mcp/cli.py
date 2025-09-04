import os, shutil, subprocess, sys


def main():
    # Prefer npm's npx to run the Node CLI we will publish.
    npx = shutil.which("npx")
    node = shutil.which("node")
    if npx:
        args = [npx, "-y", "@eyycheev/gemini-mcp"]
    elif node:
        # Fallback: try local Node dist (dev only)
        here = os.path.dirname(__file__)
        js = os.path.abspath(os.path.join(here, "..", "..", "..", "dist", "stdio.js"))
        if not os.path.exists(js):
            sys.stderr.write("npx not found and Node dist missing; install npm or build dist.\n")
            sys.exit(1)
        args = [node, js]
    else:
        sys.stderr.write("Need Node.js (node) or npm (npx) on PATH.\n")
        sys.exit(1)

    env = os.environ.copy()  # forwards GEMINI_API_KEY / GEMINI_MODEL
    proc = subprocess.Popen(args, env=env)
    proc.wait()
    sys.exit(proc.returncode)

