import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import * as msal from "@azure/msal-node";
import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

// Configuration
const isMockMode = !process.env.CLIENT_ID || process.env.CLIENT_ID === "MOCK_CLIENT_ID";

const pbiConfig = {
    clientId: process.env.CLIENT_ID || "MOCK_CLIENT_ID",
    authority: `https://login.microsoftonline.com/${process.env.TENANT_ID || "MOCK_TENANT_ID"}`,
    clientSecret: process.env.CLIENT_SECRET || "MOCK_SECRET",
    datasetId: process.env.DATASET_ID || "MOCK_DATASET_ID",
    workspaceId: process.env.WORKSPACE_ID || "MOCK_WORKSPACE_ID",
    reportId: process.env.REPORT_ID || "MOCK_REPORT_ID"
};

const msalConfig = { auth: { clientId: pbiConfig.clientId, authority: pbiConfig.authority, clientSecret: pbiConfig.clientSecret } };
const cca = new msal.ConfidentialClientApplication(msalConfig);

async function getAccessToken() {
    if (isMockMode) return "MOCK_TOKEN_12345";
    const tokenRequest = { scopes: ["https://analysis.windows.net/powerbi/api/.default"] };
    try {
        const response = await cca.acquireTokenByClientCredential(tokenRequest);
        return response.accessToken;
    } catch (error) { throw new Error(`Auth Error: ${error.message}`); }
}

async function getEmbedToken() {
    const token = await getAccessToken();
    if (isMockMode) {
        return {
            status: "success",
            mode: "mock",
            embedToken: "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCIsIklE_MOCK",
            embedUrl: "https://app.powerbi.com/reportEmbed?reportId=MOCK&mock=true",
            message: "Running in MOCK mode. Configure .env for real data."
        };
    }
    const url = `https://api.powerbi.com/v1.0/myorg/groups/${pbiConfig.workspaceId}/reports/${pbiConfig.reportId}/GenerateToken`;
    const response = await axios.post(url, { accessLevel: "View" }, { headers: { "Authorization": `Bearer ${token}` } });
    return { status: "success", mode: "real", embedToken: response.data.token, embedUrl: `https://app.powerbi.com/reportEmbed?reportId=${pbiConfig.reportId}` };
}

async function executeDaxQuery(query) {
    const token = await getAccessToken();
    if (isMockMode) {
        return {
            status: "success", mode: "mock",
            data: [
                { "Year": 2022, "Revenue": 150000 },
                { "Year": 2023, "Revenue": 200000 }
            ]
        };
    }
    const url = `https://api.powerbi.com/v1.0/myorg/datasets/${pbiConfig.datasetId}/executeQueries`;
    const response = await axios.post(url, { queries: [{ query: query }], serializerSettings: { includeNulls: true } }, { headers: { "Authorization": `Bearer ${token}` } });
    return { status: "success", mode: "real", data: response.data.results[0].tables[0].rows };
}

const server = new Server({ name: "powerbi-mcp-server", version: "0.2.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            { name: "get_powerbi_embed_token", description: "Lấy thẻ Embed Token để nhúng giao diện PowerBI vào App.", inputSchema: { type: "object", properties: {}, required: [] } },
            { name: "query_powerbi_dax", description: "Lấy dữ liệu thô (JSON Data Table) từ PowerBI qua lệnh DAX.", inputSchema: { type: "object", properties: { query: { type: "string" } }, required: ["query"] } }
        ]
    };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    try {
        if (request.params.name === "get_powerbi_embed_token") {
            const result = await getEmbedToken();
            return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        } else if (request.params.name === "query_powerbi_dax") {
            const result = await executeDaxQuery(request.params.arguments.query);
            return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
        }
        throw new Error("Tool not found");
    } catch (error) { return { content: [{ type: "text", text: `Error: ${error.message}` }], isError: true }; }
});

async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error(`PowerBI MCP server running on stdio (Mock Mode: ${isMockMode})`);
}
main().catch((error) => process.exit(1));
