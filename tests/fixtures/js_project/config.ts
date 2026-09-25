// Fixture: TypeScript configuration file
// Tests process.env access in TypeScript context

interface Config {
  databaseUrl: string;
  redisUrl: string | undefined;
  secretKey: string;
}

// process.env.KEY in TypeScript context
export const config: Config = {
  databaseUrl: process.env.DATABASE_URL as string,
  redisUrl: process.env.REDIS_URL,
  secretKey: process.env['SECRET_KEY'] as string,
};

// Also used in function context
export function getPort(): number {
  return parseInt(process.env.PORT ?? "8000", 10);
}
