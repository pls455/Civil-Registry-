"""Optional local GGUF model runner.

No network is used. If a llama.cpp-compatible executable and a local GGUF model
are present, MinhajAI can delegate generation to that model. Otherwise the
built-in deterministic engine remains fully usable.
"""
import os, subprocess

class LocalModel:
    def __init__(self, model_path="models/model.gguf", executable="llama-cli"):
        root = os.path.dirname(os.path.dirname(__file__))
        self.model_path = model_path if os.path.isabs(model_path) else os.path.join(root, model_path)
        self.executable = executable

    @property
    def available(self):
        return os.path.isfile(self.model_path) and bool(self._which(self.executable))

    def _which(self, name):
        for folder in os.environ.get("PATH", "").split(os.pathsep):
            p = os.path.join(folder, name)
            if os.path.isfile(p) and os.access(p, os.X_OK): return p
        return None

    def generate(self, prompt, max_tokens=256, temperature=0.2):
        if not self.available: return None
        cmd = [self._which(self.executable), "-m", self.model_path, "-p", prompt,
               "-n", str(max_tokens), "--temp", str(temperature), "-c", "2048"]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return p.stdout.strip() if p.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            return None
