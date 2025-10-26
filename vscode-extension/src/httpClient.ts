import * as http from 'http';

export interface HintRequest {
    file_path: string;
    code_snippet: string;
    change_type: string;
    language: string;
}

export interface HintResponse {
    success: boolean;
    hint?: string;
    error?: string;
}

function httpRequest(port: number, path: string, method: string, data?: any): Promise<any> {
    return new Promise((resolve, reject) => {
        const postData = data ? JSON.stringify(data) : undefined;

        const options = {
            hostname: 'localhost',
            port: port,
            path: path,
            method: method,
            headers: postData ? {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            } : {}
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(body));
                } catch {
                    reject(new Error('Invalid JSON response'));
                }
            });
        });

        req.on('error', reject);
        req.setTimeout(30000, () => {
            req.destroy();
            reject(new Error('Request timeout'));
        });

        if (postData) {
            req.write(postData);
        }
        req.end();
    });
}

export async function requestHint(port: number, request: HintRequest): Promise<HintResponse> {
    return await httpRequest(port, '/hint', 'POST', request);
}
