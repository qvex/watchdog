import * as vscode from 'vscode';
import * as http from 'http';
import { spawn, ChildProcess } from 'child_process';

let backendProcess: ChildProcess | null = null;

export async function checkBackendHealth(port: number): Promise<boolean> {
    return new Promise((resolve) => {
        const req = http.get(`http://localhost:${port}/health`, (res) => {
            resolve(res.statusCode === 200);
        });
        req.on('error', () => resolve(false));
        req.setTimeout(2000, () => {
            req.destroy();
            resolve(false);
        });
    });
}

export async function ensureBackendRunning(port: number, outputChannel: vscode.OutputChannel): Promise<boolean> {
    const isRunning = await checkBackendHealth(port);
    if (isRunning) {
        outputChannel.appendLine('Python backend already running');
        return true;
    }

    outputChannel.appendLine('Starting Python backend...');
    const pythonPath = 'python';
    const scriptPath = '../src/backend_server.py';

    backendProcess = spawn(pythonPath, [scriptPath, port.toString()], {
        cwd: __dirname
    });

    backendProcess.stdout?.on('data', (data) => {
        outputChannel.appendLine(`Backend: ${data.toString().trim()}`);
    });

    backendProcess.stderr?.on('data', (data) => {
        outputChannel.appendLine(`Backend Error: ${data.toString().trim()}`);
    });

    await new Promise(resolve => setTimeout(resolve, 2000));
    return await checkBackendHealth(port);
}

export function stopBackend(outputChannel: vscode.OutputChannel): void {
    if (backendProcess) {
        outputChannel.appendLine('Stopping Python backend...');
        backendProcess.kill();
        backendProcess = null;
    }
}
