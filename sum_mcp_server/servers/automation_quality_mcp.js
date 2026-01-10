#!/usr/bin/env node
/* eslint-disable @typescript-eslint/no-var-requires */

const path = require("path");

const repoRoot = path.resolve(__dirname, "..", "..");
const serverDir = path.join(repoRoot, "sum_mcp_server", "vendor", "automation-quality-mcp");

process.chdir(serverDir);
require(path.join(serverDir, "mcpServer.js"));
