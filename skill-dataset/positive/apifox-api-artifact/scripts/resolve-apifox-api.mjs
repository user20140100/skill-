#!/usr/bin/env node

import http from 'node:http';
import https from 'node:https';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const DEFAULT_BASE_URL = 'https://api.apifox.com';
const DEFAULT_ENDPOINTS_API_VERSION = 'beta-2025-09-10';
const DEFAULT_EXPORT_API_VERSION = '2024-03-28';

const HTTP_METHODS = new Set(['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']);

const stripJsonc = (content) => content.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|\s)\/\/.*$/gm, '');

const readJsonIfExists = (filePath) => {
    if (!fs.existsSync(filePath)) return null;

    try {
        return JSON.parse(stripJsonc(fs.readFileSync(filePath, 'utf8')));
    } catch {
        return null;
    }
};

const extractFlagValue = (parts, flagName) => {
    for (let index = 0; index < parts.length; index += 1) {
        const part = String(parts[index]);

        if (part === flagName) return parts[index + 1];
        if (part.startsWith(`${flagName}=`)) return part.slice(flagName.length + 1);
    }

    return undefined;
};

const getCommandParts = (serverConfig) => {
    const commandParts = typeof serverConfig.command === 'string' ? serverConfig.command.split(/\s+/).filter(Boolean) : [];
    const argParts = Array.isArray(serverConfig.args) ? serverConfig.args : [];

    return [...commandParts, ...argParts];
};

const findApifoxMcpConfig = () => {
    const configPaths = [path.join(process.cwd(), '.cursor/mcp.json'), path.join(os.homedir(), '.cursor/mcp.json')];
    const candidates = [];

    const visit = (value) => {
        if (!value || typeof value !== 'object') return;

        const serialized = JSON.stringify(value);
        if (/apifox/i.test(serialized) && (value.env?.APIFOX_ACCESS_TOKEN || /apifox-mcp-server/i.test(serialized))) {
            candidates.push(value);
        }

        Object.values(value).forEach(visit);
    };

    configPaths.map(readJsonIfExists).filter(Boolean).forEach(visit);

    for (const candidate of candidates) {
        const parts = getCommandParts(candidate);
        const token = candidate.env?.APIFOX_ACCESS_TOKEN;
        const baseUrl = extractFlagValue(parts, '--apifox-api-base-url');

        if (token || baseUrl) {
            return { token, baseUrl };
        }
    }

    return {};
};

const printUsage = () => {
    console.log(`Usage:
  node resolve-apifox-api.mjs <apifox-collaboration-url> [url2] [url3] ...

Supports single or multiple URLs. When multiple URLs from the same project
are provided, the project endpoint list is fetched only once.

Output:
  - Single URL: prints one normalized JSON object to stdout.
  - Multiple URLs: prints a JSON array of results (or errors) to stdout.

Environment:
  APIFOX_ACCESS_TOKEN       Required unless present in Cursor MCP config.
  APIFOX_API_BASE_URL       Optional. Defaults to Cursor MCP config or ${DEFAULT_BASE_URL}.
  APIFOX_ENDPOINTS_VERSION  Optional. Defaults to ${DEFAULT_ENDPOINTS_API_VERSION}.
  APIFOX_EXPORT_VERSION     Optional. Defaults to ${DEFAULT_EXPORT_API_VERSION}.
`);
};

const fail = (message, detail) => {
    const payload = { error: message };
    if (detail) payload.detail = detail;
    console.error(JSON.stringify(payload, null, 2));
    process.exit(1);
};

const parseArgs = () => {
    const inputs = process.argv.slice(2).filter((arg) => arg !== '-h' && arg !== '--help');

    if (inputs.length === 0 || process.argv.includes('-h') || process.argv.includes('--help')) {
        printUsage();
        process.exit(inputs.length === 0 ? 1 : 0);
    }

    return { inputs };
};

const parseApifoxLink = (input) => {
    const match = input.match(/\/link\/project\/(\d+)\/apis\/api-(\d+)/);
    if (!match) {
        fail('Unsupported Apifox collaboration link. Expected /link/project/{projectId}/apis/api-{apiId}.');
    }

    return {
        projectId: Number(match[1]),
        apiId: Number(match[2]),
    };
};

const requestJson = (url, options = {}) =>
    new Promise((resolve, reject) => {
        const parsedUrl = new URL(url);
        const transport = parsedUrl.protocol === 'http:' ? http : https;
        const body = options.body ? JSON.stringify(options.body) : undefined;

        const request = transport.request(
            parsedUrl,
            {
                method: options.method || 'GET',
                headers: {
                    Accept: 'application/json',
                    ...(body ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) } : {}),
                    ...(options.headers || {}),
                },
            },
            (response) => {
                const chunks = [];
                response.on('data', (chunk) => chunks.push(chunk));
                response.on('end', () => {
                    const text = Buffer.concat(chunks).toString('utf8');
                    let data = null;

                    if (text) {
                        try {
                            data = JSON.parse(text);
                        } catch (error) {
                            reject(new Error(`Failed to parse JSON response from ${url}: ${error.message}. Response: ${text.slice(0, 500)}`));
                            return;
                        }
                    }

                    if (response.statusCode < 200 || response.statusCode >= 300) {
                        const error = new Error(`HTTP ${response.statusCode} from ${url}`);
                        error.statusCode = response.statusCode;
                        error.response = data;
                        reject(error);
                        return;
                    }

                    resolve(data);
                });
            },
        );

        request.on('error', reject);
        if (body) request.write(body);
        request.end();
    });

const parseJsonValue = (value) => {
    if (typeof value !== 'string') return value;

    try {
        return JSON.parse(value);
    } catch {
        return value;
    }
};

const chooseSuccessfulResponse = (responses = []) => {
    if (!Array.isArray(responses) || responses.length === 0) return null;

    return (
        responses.find((response) => String(response.code) === '200') ||
        responses.find((response) => /^2\d\d$|^2XX$/i.test(String(response.code))) ||
        responses[0]
    );
};

const chooseOasSuccessfulResponse = (responses = {}) => {
    const entries = Object.entries(responses);
    if (entries.length === 0) return null;

    const found = entries.find(([statusCode]) => statusCode === '200') || entries.find(([statusCode]) => /^2\d\d$|^2XX$/i.test(statusCode)) || entries[0];

    return found ? { statusCode: found[0], response: found[1] } : null;
};

const getOasJsonContent = (content = {}) =>
    content['application/json'] ||
    content['application/*+json'] ||
    Object.entries(content).find(([mediaType]) => mediaType.includes('json'))?.[1] ||
    Object.values(content)[0] ||
    null;

const getOasExample = (media) => {
    if (!media) return undefined;
    if (Object.prototype.hasOwnProperty.call(media, 'example')) return media.example;

    const firstExample = media.examples && Object.values(media.examples)[0];
    if (!firstExample) return undefined;
    if (Object.prototype.hasOwnProperty.call(firstExample, 'value')) return firstExample.value;
    return parseJsonValue(firstExample.externalValue || firstExample.summary);
};

const normalizeEndpoint = ({ endpoint, projectId, apiId, source }) => {
    const successfulResponse = chooseSuccessfulResponse(endpoint.responses);
    const firstResponseExample = successfulResponse?.responseExamples?.[0];

    return {
        source,
        projectId,
        apiId,
        id: endpoint.id,
        name: endpoint.name,
        method: String(endpoint.method || '').toLowerCase(),
        path: endpoint.path,
        description: endpoint.description || '',
        tags: endpoint.tags || [],
        service_name: endpoint.tags?.[0],
        request_schema: {
            body: endpoint.requestBody?.schema || null,
            parameters: endpoint.parameters || { query: [], path: [], header: [], cookie: [] },
        },
        response_schema: successfulResponse?.schema || null,
        response_example: parseJsonValue(firstResponseExample?.data),
        response_status_code: Number(successfulResponse?.code) || 200,
        raw_endpoint: endpoint,
    };
};

const normalizeOpenApi = ({ openapi, projectId, apiId, source }) => {
    for (const [path, pathItem] of Object.entries(openapi.paths || {})) {
        for (const [method, operation] of Object.entries(pathItem || {})) {
            if (!HTTP_METHODS.has(method)) continue;

            const requestMedia = getOasJsonContent(operation.requestBody?.content);
            const successfulResponse = chooseOasSuccessfulResponse(operation.responses);
            const responseMedia = getOasJsonContent(successfulResponse?.response?.content);

            return {
                source,
                projectId,
                apiId,
                name: operation.summary || operation.operationId || `${method.toUpperCase()} ${path}`,
                method,
                path,
                description: operation.description || '',
                tags: operation.tags || [],
                service_name: operation.tags?.[0],
                request_schema: {
                    body: requestMedia?.schema || null,
                    parameters: operation.parameters || [],
                },
                response_schema: responseMedia?.schema || null,
                response_example: getOasExample(responseMedia),
                response_status_code: Number(successfulResponse?.statusCode) || 200,
                raw_openapi: openapi,
            };
        }
    }

    fail('Selected endpoint export succeeded, but no HTTP operation was found in the OpenAPI document.');
};

const listProjectEndpoints = async ({ baseUrl, token, endpointsApiVersion, projectId }) => {
    const url = new URL(`/projects/${projectId}/http-endpoints`, baseUrl);

    const payload = await requestJson(url.toString(), {
        headers: {
            Authorization: `Bearer ${token}`,
            'X-Apidog-Api-Version': endpointsApiVersion,
        },
    });

    return Array.isArray(payload?.data) ? payload.data : [];
};

const exportSelectedEndpointOpenApi = async ({ baseUrl, token, exportApiVersion, projectId, apiId }) => {
    const url = new URL(`/v1/projects/${projectId}/export-openapi?locale=zh-CN`, baseUrl);

    return requestJson(url.toString(), {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${token}`,
            'X-Apifox-Api-Version': exportApiVersion,
        },
        body: {
            scope: {
                type: 'SELECTED_ENDPOINTS',
                selectedEndpointIds: [apiId],
            },
            options: {
                includeApifoxExtensionProperties: true,
                addFoldersToTags: true,
            },
            oasVersion: '3.1',
            exportFormat: 'JSON',
        },
    });
};

const resolveOne = async ({ projectId, apiId, endpointsCache, config }) => {
    const { baseUrl, token, endpointsApiVersion, exportApiVersion } = config;

    // Try from cached endpoint list first
    const cached = endpointsCache.get(projectId);
    if (cached) {
        const endpoint = cached.find((item) => Number(item.id) === apiId);
        if (endpoint) {
            return normalizeEndpoint({ endpoint, projectId, apiId, source: 'apifox-openapi:http-endpoints' });
        }
    }

    // Fallback: export single endpoint OpenAPI
    try {
        const openapi = await exportSelectedEndpointOpenApi({ baseUrl, token, exportApiVersion, projectId, apiId });
        return normalizeOpenApi({ openapi, projectId, apiId, source: 'apifox-openapi:export-openapi' });
    } catch (error) {
        return { error: `Failed to resolve apiId ${apiId} in project ${projectId}`, detail: error.response || error.message };
    }
};

const main = async () => {
    const { inputs } = parseArgs();
    const isBatch = inputs.length > 1;

    // Parse all links
    const parsed = inputs.map((input) => {
        const match = input.match(/\/link\/project\/(\d+)\/apis\/api-(\d+)/);
        if (!match) {
            return { input, error: `Unsupported link format: ${input}` };
        }
        return { input, projectId: Number(match[1]), apiId: Number(match[2]) };
    });

    // Check for parse errors in single mode
    if (!isBatch && parsed[0].error) {
        fail(parsed[0].error);
    }

    const mcpConfig = findApifoxMcpConfig();
    const config = {
        token: process.env.APIFOX_ACCESS_TOKEN || mcpConfig.token,
        baseUrl: process.env.APIFOX_API_BASE_URL || mcpConfig.baseUrl || DEFAULT_BASE_URL,
        endpointsApiVersion: process.env.APIFOX_ENDPOINTS_VERSION || DEFAULT_ENDPOINTS_API_VERSION,
        exportApiVersion: process.env.APIFOX_EXPORT_VERSION || DEFAULT_EXPORT_API_VERSION,
    };

    if (!config.token) {
        fail('Missing APIFOX_ACCESS_TOKEN. Create an Apifox personal access token and expose it as an environment variable, or configure it in Cursor MCP.');
    }

    // Group by projectId and fetch endpoint lists once per project
    const projectIds = [...new Set(parsed.filter((p) => p.projectId).map((p) => p.projectId))];
    const endpointsCache = new Map();

    for (const projectId of projectIds) {
        try {
            const endpoints = await listProjectEndpoints({
                baseUrl: config.baseUrl,
                token: config.token,
                endpointsApiVersion: config.endpointsApiVersion,
                projectId,
            });
            endpointsCache.set(projectId, endpoints);
        } catch (error) {
            if (process.env.APIFOX_RESOLVER_DEBUG === '1') {
                console.error(
                    JSON.stringify(
                        {
                            warning: `Failed to list endpoints for project ${projectId}. Will fall back to per-endpoint export.`,
                            detail: error.response || error.message,
                        },
                        null,
                        2,
                    ),
                );
            }
            endpointsCache.set(projectId, []);
        }
    }

    // Resolve each input
    const results = [];
    for (const item of parsed) {
        if (item.error) {
            results.push({ input: item.input, error: item.error });
            continue;
        }
        const result = await resolveOne({ projectId: item.projectId, apiId: item.apiId, endpointsCache, config });
        results.push(result);
    }

    // Output
    if (isBatch) {
        console.log(JSON.stringify(results, null, 2));
    } else {
        const single = results[0];
        if (single.error) {
            fail(single.error, single.detail);
        }
        console.log(JSON.stringify(single, null, 2));
    }
};

main();
