# Troubleshooting Database Connection Issues

This document provides guidance for resolving common issues with database connections in Chat2DB, particularly the "no tables found" error.

## Common Issues and Solutions

### 1. "No tables found" Error

#### Symptoms
- When selecting a database connection, the system shows "该数据库中没有找到表" (No tables found in the database)
- Tables exist in the database but are not displayed in the UI

#### Root Causes and Solutions

1. **Connection Configuration Issues**
   - Verify all connection parameters (host, port, username, password, database name)
   - Ensure the database type is correctly selected (MySQL, PostgreSQL, SQLite)
   - Test the connection using the "测试连接" (Test Connection) button

2. **Insufficient Database Permissions**
   - The database user may not have permissions to query system tables
   - For MySQL, ensure the user has SELECT privileges on `information_schema.tables`
   - For PostgreSQL, ensure the user has access to `pg_tables`
   - For SQLite, ensure the file is readable and contains tables

3. **Network Connectivity Issues**
   - Verify that the database server is accessible from the Chat2DB container
   - Check firewall settings and network connectivity
   - Ensure the database port is open and accessible

4. **Database Driver Issues**
   - Verify that the required database drivers are installed
   - Check the backend logs for driver-related errors

### 2. Connection Test Fails

#### Enhanced Connection Testing
The updated connection test now performs two checks:
1. Basic connectivity test (SELECT 1)
2. Table query permissions test

If the basic connection succeeds but table query fails, the system will provide a detailed error message.

### 3. Error Message Interpretation

#### Backend Error Messages
- "Failed to create engine for database type" - Invalid connection parameters
- "Failed to connect to database" - Network or authentication issues
- "Failed to query tables" - Permission or query issues
- "Unsupported database type" - Incorrect database type selection

#### Frontend Error Display
The updated table manager now displays detailed error messages directly in the UI, making it easier to diagnose issues.

## Best Practices

### Connection Configuration
1. Always test connections before using them
2. Use specific database users with minimal required permissions
3. Verify network connectivity to database servers
4. Check firewall and security group settings

### Database Permissions
1. For MySQL:
   ```sql
   GRANT SELECT ON information_schema.tables TO 'chat2db_user'@'%';
   ```
2. For PostgreSQL:
   ```sql
   GRANT USAGE ON SCHEMA public TO chat2db_user;
   ```
3. For SQLite:
   Ensure the database file is readable by the application

### Debugging Steps
1. Check backend logs for detailed error messages
2. Test database connectivity using command-line tools
3. Verify database user permissions
4. Confirm network accessibility

## Contact Support
If you continue to experience issues after following this guide, please provide:
1. The exact error message displayed
2. Backend log entries related to the error
3. Your database connection configuration (without sensitive information)
4. Steps to reproduce the issue