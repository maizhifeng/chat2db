export interface DatabaseConnection {
  id: string;
  name: string;
  type: string; // mysql, postgresql, sqlite, etc.
  host: string;
  port: number;
  username: string;
  password: string;
  database: string;
  environment: string; // dev, test, prod
  file_path: string; // for CSV files
}