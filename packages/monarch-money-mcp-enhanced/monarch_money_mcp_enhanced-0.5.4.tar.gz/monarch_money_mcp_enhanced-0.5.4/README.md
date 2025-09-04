# Monarch Money MCP Server Enhanced

A dynamic MCP (Model Context Protocol) server that automatically exposes **all** methods from the `monarchmoney-enhanced` library as MCP tools. No manual updates needed when the library adds new features!

**Version**: 0.3.4 (synchronized with `monarchmoney-enhanced`)

## Key Features

🔄 **Fully Dynamic**: Automatically discovers and exposes all MonarchMoney methods as tools  
🚀 **Auto-Updating**: GitHub Actions automatically release new versions when `monarchmoney-enhanced` updates  
📊 **Complete API Access**: Every method in the library becomes an MCP tool automatically  
🛠️ **Smart Schema Generation**: Automatically generates parameter schemas from method signatures  

## Automatically Available Features

Since this server dynamically exposes all `monarchmoney-enhanced` methods, you get access to **everything**:

- **Account Management**: Create, update, delete accounts, get balances, history
- **Transaction Operations**: CRUD operations, categorization, tagging, rules, splits
- **Budget Management**: Set budgets, analyze spending, track goals
- **Category & Tag Management**: Create, modify, delete categories and tags
- **Institution Management**: Manage connected financial institutions
- **Recurring Transactions**: Track and manage recurring payments
- **Investment Tracking**: Portfolio holdings, performance data
- **Subscription Management**: Account details and billing info
- **And more...**: Any new features added to `monarchmoney-enhanced` are instantly available!

## Installation

1. Clone or download this MCP server
2. Install dependencies:
   ```bash
   cd /path/to/monarch-money-mcp
   uv sync
   ```

## Configuration

Add the server to your `.mcp.json` configuration file:

```json
{
  "mcpServers": {
    "monarch-money-enhanced": {
      "command": "/path/to/uv",
      "args": [
        "--directory", 
        "/path/to/monarch-money-mcp-enhanced",
        "run",
        "python",
        "server.py"
      ],
      "env": {
        "MONARCH_EMAIL": "your-email@example.com",
        "MONARCH_PASSWORD": "your-password",
        "MONARCH_MFA_SECRET": "your-mfa-secret-key"
      }
    }
  }
}
```

**Important Notes:**
- Replace `/path/to/uv` with the full path to your `uv` executable (find it with `which uv`)
- Replace `/path/to/monarch-money-mcp-enhanced` with the absolute path to this server directory
- Use absolute paths, not relative paths

### Getting Your MFA Secret

1. Go to Monarch Money settings and enable 2FA
2. When shown the QR code, look for the "Can't scan?" or "Enter manually" option
3. Copy the secret key (it will be a string like `T5SPVJIBRNPNNINFSH5W7RFVF2XYADYX`)
4. Use this as your `MONARCH_MFA_SECRET`

## How It Works

The server automatically discovers all public methods from the `monarchmoney-enhanced` library and creates MCP tools for them. This means:

1. **No Manual Tool Definitions**: Methods are discovered at runtime
2. **Automatic Schema Generation**: Parameter types and requirements are inferred from method signatures  
3. **Instant Updates**: When `monarchmoney-enhanced` adds new methods, they become available immediately
4. **Complete Coverage**: Every public method becomes an MCP tool

## Available Tools (Dynamic)

Instead of listing specific tools, here's how to see what's available:

1. **Runtime Discovery**: The server lists all available tools when it starts
2. **Method Coverage**: All public methods from `MonarchMoney` class become tools
3. **Automatic Documentation**: Tool descriptions are generated from method docstrings

### Example Tools (Auto-Generated)

Some examples of tools that are automatically created:

- `get_accounts` - Retrieve all linked financial accounts
- `create_transaction` - Creates a transaction with the given parameters  
- `create_transaction_category` - Creates a new transaction category
- `get_transaction_tags` - Get all transaction tags
- `set_budget_amount` - Set budget amount for a category
- `get_merchants` - Get all merchants
- `delete_transaction` - Deletes the given transaction
- `get_recurring_transactions` - Get all recurring transactions
- `create_manual_account` - Creates a new manual account
- **And 30+ more...** (automatically updated as the library grows)

## Usage Examples

### Creating Transaction Categories
```
Use create_transaction_category with name "Shared - Telco" to create a new category for shared telecom expenses.
```

### Applying Transaction Rules  
```
Use the transaction management tools to automatically categorize transactions. For example:
- Find transactions containing "Sentris Network LLC" 
- Update them to use the "Shared - Telco" category
```

### Complete Financial Management
```
Since all MonarchMoney methods are available:
- Create and manage accounts with create_manual_account
- Set up budgets with set_budget_amount  
- Tag transactions with set_transaction_tags
- Analyze spending patterns with get_cashflow_summary
- Track investments with get_account_holdings
```

## Session Management

The server automatically manages authentication sessions:
- Sessions are cached in a `.mm` directory for faster subsequent logins
- The session cache is automatically created and managed
- Use `MONARCH_FORCE_LOGIN=true` in the env section to force a fresh login if needed

## Troubleshooting

### MFA Issues
- Ensure your MFA secret is correct and properly formatted
- Try setting `MONARCH_FORCE_LOGIN=true` in your `.mcp.json` env section
- Check that your system time is accurate (required for TOTP)

### Connection Issues
- Verify your email and password are correct in `.mcp.json`
- Check your internet connection
- Try running the server directly to see detailed error messages:
  ```bash
  uv run server.py
  ```

### Session Problems
- Delete the `.mm` directory to clear cached sessions
- Set `MONARCH_FORCE_LOGIN=true` in your `.mcp.json` env section temporarily

## Auto-Updates

This repository includes GitHub Actions that automatically:

1. **Monitor Updates**: Checks every 6 hours for new `monarchmoney-enhanced` releases
2. **Auto-Release**: Creates new releases when the library updates  
3. **Zero Maintenance**: No manual intervention needed to get new features
4. **Dependency Management**: Dependabot keeps other dependencies secure

## Credits

### Original MCP Server
- **Author**: Taurus Colvin ([@colvint](https://github.com/colvint))
- **Repository**: [https://github.com/colvint/monarch-money-mcp](https://github.com/colvint/monarch-money-mcp)

### Enhanced MCP Server
- **Enhanced By**: Keith Herrington ([@keithah](https://github.com/keithah))
- **Repository**: [https://github.com/keithah/monarch-money-mcp-enhanced](https://github.com/keithah/monarch-money-mcp-enhanced)
- **Name**: `monarch-money-mcp-enhanced`
- **Version**: Synchronized with `monarchmoney-enhanced` library
- **Features**: Dynamic tool generation, auto-updates, complete API coverage

### MonarchMoney Enhanced Library
- **Enhanced By**: Keith Herrington ([@keithah](https://github.com/keithah))
- **Repository**: [https://github.com/keithah/monarchmoney-enhanced](https://github.com/keithah/monarchmoney-enhanced)
- **Description**: Enhanced version of the MonarchMoney Python library with additional features

### Original MonarchMoney Python Library
- **Author**: hammem ([@hammem](https://github.com/hammem))
- **Repository**: [https://github.com/hammem/monarchmoney](https://github.com/hammem/monarchmoney)
- **License**: MIT License

This dynamic MCP server automatically adapts to library changes, providing seamless integration with AI assistants through the Model Context Protocol.

## Security Notes

- Keep your credentials secure in your `.mcp.json` file
- The MFA secret provides full access to your account - treat it like a password
- Session files in `.mm` directory contain authentication tokens - keep them secure
- Consider restricting access to your `.mcp.json` file since it contains sensitive credentials