#!/usr/bin/env node
import readline from "node:readline";
import axios from "axios";

const MCP_HTTP_URL = process.env.MCP_HTTP_URL || "http://localhost:3000/mcp";
const MCP_BEARER   = process.env.MCP_BEARER || "";

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
const write = (o) => process.stdout.write(JSON.stringify(o) + "\n");

rl.on("line", async (line) => {
  if (!line.trim()) return;
  let msg; try { msg = JSON.parse(line); } catch { return; }
  try {
    const res = await axios.post(MCP_HTTP_URL, msg, {
      headers: {
        "Content-Type": "application/json",
        ...(MCP_BEARER ? { Authorization: `Bearer ${MCP_BEARER}` } : {})
      },
      timeout: 30000
    });
    write(res.data);
  } catch (err) {
    write({
      jsonrpc: "2.0",
      id: msg.id ?? null,
      error: { code: -32099, message: `Bridge error: ${err?.message || "unknown"}` }
    });
  }
});
