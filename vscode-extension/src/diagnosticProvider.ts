import * as vscode from 'vscode';
import { requestHint, HintRequest } from './httpClient';

let diagnosticCollection: vscode.DiagnosticCollection;
let debounceTimer: NodeJS.Timeout | null = null;
const DEBOUNCE_MS = 2000;

export function activate(context: vscode.ExtensionContext, port: number, outputChannel: vscode.OutputChannel) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('watchdog');
    context.subscriptions.push(diagnosticCollection);

    vscode.workspace.onDidChangeTextDocument(event => {
        if (event.document.languageId !== 'python') {
            return;
        }

        if (debounceTimer) {
            clearTimeout(debounceTimer);
        }

        debounceTimer = setTimeout(() => {
            analyzeDocument(event.document, port, outputChannel);
        }, DEBOUNCE_MS);
    });
}

async function analyzeDocument(document: vscode.TextDocument, port: number, outputChannel: vscode.OutputChannel) {
    try {
        const text = document.getText();
        if (text.trim().length === 0) {
            return;
        }

        const request: HintRequest = {
            file_path: document.fileName,
            code_snippet: text,
            change_type: 'modification',
            language: 'python'
        };

        const response = await requestHint(port, request);

        if (response.success && response.hint) {
            const range = new vscode.Range(0, 0, 0, 0);
            const diagnostic = new vscode.Diagnostic(
                range,
                response.hint,
                vscode.DiagnosticSeverity.Information
            );
            diagnostic.source = 'Watchdog';
            diagnosticCollection.set(document.uri, [diagnostic]);
        }
    } catch (error) {
        outputChannel.appendLine(`Diagnostic error: ${error}`);
    }
}

export function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
}
