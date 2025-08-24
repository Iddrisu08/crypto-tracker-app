# MCP Setup Guide for Crypto Tracker

## 🚀 Step 1: Install Playwright Dependencies

```bash
cd crypto-tracker-frontend
npm install --save-dev @playwright/test
npx playwright install
```

## 🔧 Step 2: Install MCP Servers

### Install Required Tools
```bash
# Install filesystem MCP server
npm install -g @modelcontextprotocol/server-filesystem

# Install Playwright MCP (if available)
npm install -g @playwright/test

# Install uv for Serena MCP (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# OR on macOS with Homebrew:
# brew install uv
```

### Install Serena MCP
```bash
# Option 1: Direct installation via uvx (recommended)
uvx --from git+https://github.com/oraios/serena serena-mcp-server

# Option 2: Clone and install locally
git clone https://github.com/oraios/serena
cd serena
uv run serena-mcp-server
```

## 📱 Step 3: Configure Claude Desktop

1. **Find your Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add this configuration:**

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server"
      ],
      "cwd": "/Users/iddrisuabdulrazakiddrisu/crypto-tracker-project"
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/test", "--config=playwright.config.js"],
      "cwd": "/Users/iddrisuabdulrazakiddrisu/crypto-tracker-project/crypto-tracker-frontend",
      "env": {
        "NODE_ENV": "test"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/iddrisuabdulrazakiddrisu/crypto-tracker-project"],
      "env": {}
    }
  }
}
```

## 🧪 Step 4: Test Your Setup

### Manual Test (without MCP):
```bash
cd crypto-tracker-frontend
npx playwright test
```

### With MCP in Claude Desktop:
After restarting Claude Desktop, you should be able to:

1. **Run Tests**: "Run my Playwright tests for the analytics dashboard"
2. **Take Screenshots**: "Take a screenshot of the portfolio page"
3. **Check Code**: "Review my React components for best practices"
4. **Debug Issues**: "Test the portfolio refresh functionality"

## 🔍 Available Test Commands

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/portfolio.spec.js

# Run tests with UI
npx playwright test --ui

# Run tests in headed mode (see browser)
npx playwright test --headed

# Generate test report
npx playwright show-report
```

## 📊 Test Coverage

The tests cover:
- ✅ Portfolio overview display
- ✅ Analytics dashboard functionality
- ✅ Transaction form validation
- ✅ Refresh button functionality
- ✅ Chart rendering
- ✅ Error handling
- ✅ Mobile responsiveness

## 🎯 Using MCPs for Development

### With Playwright MCP:
- **"Test my portfolio refresh button"**
- **"Check if the analytics charts load correctly"**
- **"Test the transaction form validation"**
- **"Take screenshots for documentation"**

### With Serena MCP (Code Analysis & Editing):
- **"Review my React components for best practices"**
- **"Refactor this function for better performance"**
- **"Find security vulnerabilities in my code"**
- **"Suggest TypeScript improvements"**
- **"Optimize my database queries"**
- **"Generate unit tests for my functions"**

### With Filesystem MCP:
- **"Review my React component structure"**
- **"Suggest improvements for my API endpoints"**
- **"Help optimize my portfolio calculations"**
- **"Generate documentation for my functions"**

## 🚨 Troubleshooting

### If tests fail:
1. Ensure both servers are running (frontend on 5173, backend on 5001)
2. Check that the backend API endpoints are responding
3. Verify test timeouts are sufficient for your system

### If MCP doesn't connect:
1. Restart Claude Desktop after config changes
2. Check the config file path is correct
3. Verify all npm packages are installed
4. Check terminal for error messages

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Claude can run your tests
- ✅ Claude can take screenshots
- ✅ Claude can read your code files
- ✅ Claude can suggest improvements
- ✅ Test reports are generated automatically

Now you have professional-grade testing and development assistance! 🚀