import { spawn, ChildProcess } from "child_process";
import { existsSync } from "fs";
import { resolve } from "path";

function streamLogs(child: ChildProcess, prefix: string) {
  child.stdout?.on("data", (data) => {
    const lines = data.toString().split("\n");
    for (const line of lines) {
      if (line.trim()) {
        console.log(`[${prefix}] ${line}`);
      }
    }
  });

  child.stderr?.on("data", (data) => {
    const lines = data.toString().split("\n");
    for (const line of lines) {
      if (line.trim()) {
        console.error(`[${prefix} ERROR] ${line}`);
      }
    }
  });
}

async function start() {
  console.log("[Orchestrator] Starting Griffin Core services...");

  const backendEnv = {
    ...process.env,
    PYTHONPATH: ".",
  };

  console.log(`[Orchestrator] Launching FastAPI backend on port 8001...`);
  
  let backendProcess: ChildProcess;
  const venvPython = resolve("./venv/bin/python");
  
  if (existsSync(venvPython)) {
    console.log("[Orchestrator] Found python virtual environment. Launching backend...");
    backendProcess = spawn(venvPython, ["backend/main.py"], {
      env: backendEnv,
    });
  } else {
    console.log("[Orchestrator] Virtual environment missing. Recreating venv and installing packages...");
    backendProcess = spawn("bash", [
      "-c",
      "if ! dpkg -s python3-venv >/dev/null 2>&1; then DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y python3-venv; fi && python3 -m venv venv && source venv/bin/activate && pip install --no-cache-dir fastapi uvicorn sqlalchemy python-multipart pymysql cryptography && pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && pip install --no-cache-dir -r requirements.txt && PYTHONPATH=. python backend/main.py"
    ], {
      env: backendEnv,
    });
  }

  streamLogs(backendProcess, "Backend");

  backendProcess.on("close", (code) => {
    console.log(`[Orchestrator] Backend process exited with code ${code}`);
    cleanup(code || 0);
  });

  console.log("[Orchestrator] Starting Vite frontend on port 3000...");
  const frontendProcess = spawn("npx", ["vite", "--host", "0.0.0.0", "--port", "3000"], {
    env: process.env,
    shell: true,
  });

  streamLogs(frontendProcess, "Frontend");

  frontendProcess.on("close", (code) => {
    console.log(`[Orchestrator] Frontend process exited with code ${code}`);
    cleanup(code || 0);
  });

  let isShuttingDown = false;
  function cleanup(exitCode: number = 0) {
    if (isShuttingDown) return;
    isShuttingDown = true;
    console.log("[Orchestrator] Initiating graceful teardown...");

    try {
      backendProcess.kill("SIGTERM");
    } catch {
      // Ignore errors during process termination
    }
    
    try {
      frontendProcess.kill("SIGTERM");
    } catch {
      // Ignore errors during process termination
    }

    setTimeout(() => {
      process.exit(exitCode);
    }, 1000);
  }

  process.on("SIGINT", () => cleanup(0));
  process.on("SIGTERM", () => cleanup(0));
}

start().catch((err) => {
  console.error("[Orchestrator] Fatal startup error:", err);
  process.exit(1);
});
