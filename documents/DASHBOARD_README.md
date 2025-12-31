# Turbo Dashboard

A modern, AI-powered business intelligence dashboard for analyzing Turbo.az car listings data.

## Features

- **Authentication & Authorization**: Secure login with NextAuth.js, role-based access control
- **Admin Panel**: Full CRUD operations for user management
- **Landing Page**: Professional, business-focused homepage
- **Business Dashboard**: Real-time analytics, charts, and insights
- **AI-Powered Queries**: Ask questions in natural language using Gemini AI
- **SQL Query Execution**: Run custom SQL queries with real-time chart visualization
- **Interactive Charts**: Beautiful visualizations with Recharts
- **Responsive Design**: Mobile-first, modern UI with Tailwind CSS

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Database**: PostgreSQL (existing Turbo.az database)
- **ORM**: Prisma
- **Authentication**: NextAuth.js v5
- **AI**: Google Gemini API
- **UI**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts

## Project Structure

```
turbo-dashboard/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication pages
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/              # Protected dashboard pages
│   │   ├── dashboard/            # Main dashboard
│   │   └── admin/                # Admin panel
│   ├── api/                      # API routes
│   │   ├── auth/[...nextauth]/   # NextAuth endpoint
│   │   ├── ai/                   # Gemini AI endpoints
│   │   └── users/                # User CRUD endpoints
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Landing page
│   └── globals.css               # Global styles
├── components/                   # React components
│   └── ui/                       # shadcn/ui components
├── lib/                          # Utilities
│   ├── auth.ts                   # NextAuth configuration
│   ├── prisma.ts                 # Prisma client
│   ├── gemini.ts                 # Gemini AI utilities
│   └── utils.ts                  # Helper functions
├── prisma/
│   └── schema.prisma             # Database schema
├── types/
│   └── next-auth.d.ts            # Type declarations
├── .env                          # Environment variables
├── package.json                  # Dependencies
└── tsconfig.json                 # TypeScript config
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- PostgreSQL database (already set up with Turbo.az data)
- Gemini API key

### Installation

1. **Install dependencies**:
   ```bash
   cd /Users/ismatsamadov/turbo-dashboard
   npm install
   ```

2. **Generate Prisma Client**:
   ```bash
   npx prisma generate
   ```

3. **Push database schema** (creates users table):
   ```bash
   npx prisma db push
   ```

4. **Create admin user** (optional):
   ```bash
   # Run this SQL in your PostgreSQL database
   # Password: admin123 (hashed with bcrypt)
   INSERT INTO users (id, email, password, name, role)
   VALUES (
     'admin-1',
     'admin@turbo.az',
     '$2a$10$XxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx',
     'Admin User',
     'admin'
   );
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

6. **Open browser**:
   ```
   http://localhost:3000
   ```

## Environment Variables

The `.env` file is already configured with:

```env
DATABASE_URL="postgresql://..."
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-change-this-in-production"
GEMINI_API_KEY="AIzaSyCjzRCVEKUrWoLwzFwa1YoBekcplh8rHLs"
```

⚠️ **Important**: Change `NEXTAUTH_SECRET` in production!

## Key Features

### 1. Authentication System

- **Login/Register**: Secure authentication with bcrypt password hashing
- **Role-Based Access**: `admin` and `user` roles
- **Protected Routes**: Dashboard and admin panel require authentication
- **Session Management**: JWT-based sessions with NextAuth

### 2. Admin Panel (`/admin`)

- **User List**: View all users with pagination
- **Create User**: Add new users with email/password
- **Edit User**: Update user details and roles
- **Delete User**: Remove users from the system
- **Role Management**: Assign admin or user roles

### 3. Business Dashboard (`/dashboard`)

- **Overview Cards**: Total listings, average price, popular makes
- **Charts**: Interactive visualizations of market data
- **Filters**: Filter by make, model, year, price range
- **Real-time Stats**: Updated statistics from the database

### 4. AI-Powered Query System

**Natural Language Queries**:
- "How many cars are there?"
- "What are the top 5 most popular car makes?"
- "Show me average price by manufacturer"
- "How many listings in Bakı?"

**Features**:
- Automatic SQL generation from natural language
- Query execution against live database
- Auto-detect chart type (bar, line, pie, table)
- Interactive chart visualization
- Query history and results export

### 5. SQL Query Execution

- **Custom Queries**: Run any SQL query against the database
- **Syntax Highlighting**: SQL code editor
- **Results Table**: Display query results in a table
- **Chart Visualization**: Automatically visualize data as charts
- **Export Results**: Download results as CSV or JSON

## Database Schema

### Users Table (new)

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT,
  role TEXT DEFAULT 'user',
  image TEXT,
  email_verified TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Turbo Listings Table (existing)

The dashboard connects to your existing `scraping.turbo_az` table with 13,000+ car listings.

## API Endpoints

### Authentication
- `POST /api/auth/signin` - Login
- `POST /api/auth/signout` - Logout
- `POST /api/auth/signup` - Register

### Users (Admin only)
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### AI Queries
- `POST /api/ai/query` - Natural language query
- `POST /api/ai/execute-sql` - Execute SQL query

## Gemini AI Integration

The dashboard uses Google Gemini Pro to:

1. **Understand Database Schema**: Gemini is provided with complete schema documentation
2. **Generate SQL**: Converts natural language to valid PostgreSQL queries
3. **Explain Results**: Provides human-friendly explanations of data
4. **Detect Chart Types**: Automatically suggests best chart type for data

**Example Flow**:
```
User: "Show me top 10 car makes by listing count"
  ↓
Gemini: Generates SQL → SELECT make, COUNT(*) as count FROM scraping.turbo_az GROUP BY make ORDER BY count DESC LIMIT 10
  ↓
Execute: Runs query against database
  ↓
Visualize: Creates bar chart with results
  ↓
Explain: "The data shows BMW has the most listings with 1,234 cars, followed by Mercedes..."
```

## Deployment

### Production Build

```bash
npm run build
npm start
```

### Deploy to Vercel

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Environment Variables for Production

- `DATABASE_URL` - PostgreSQL connection string
- `NEXTAUTH_URL` - Production URL (e.g., https://yourdomain.com)
- `NEXTAUTH_SECRET` - Generate with `openssl rand -base64 32`
- `GEMINI_API_KEY` - Your Gemini API key

## Development Workflow

1. **Database Changes**:
   ```bash
   # Edit prisma/schema.prisma
   npx prisma db push
   npx prisma generate
   ```

2. **Add UI Components**:
   ```bash
   # shadcn/ui components are in components/ui/
   # Add new components as needed
   ```

3. **Add API Routes**:
   ```bash
   # Create files in app/api/
   # Use Server Actions or API routes
   ```

## Common Tasks

### Create a New User (via SQL)

```sql
-- Password: yourpassword (hash it first with bcrypt)
INSERT INTO users (id, email, password, name, role)
VALUES (
  'unique-id',
  'user@example.com',
  '$2a$10$...',  -- bcrypt hash
  'User Name',
  'user'
);
```

### Reset Admin Password

```sql
UPDATE users
SET password = '$2a$10$...'  -- new bcrypt hash
WHERE email = 'admin@turbo.az';
```

### Query Turbo Listings

```sql
-- Total listings
SELECT COUNT(*) FROM scraping.turbo_az;

-- Listings by make
SELECT make, COUNT(*) as count
FROM scraping.turbo_az
GROUP BY make
ORDER BY count DESC
LIMIT 10;

-- Average year by make
SELECT make, AVG(year)::int as avg_year
FROM scraping.turbo_az
WHERE year IS NOT NULL
GROUP BY make
ORDER BY avg_year DESC;
```

## Troubleshooting

### Database Connection Issues

- Check `DATABASE_URL` in `.env`
- Verify PostgreSQL is running
- Test connection: `npx prisma studio`

### Authentication Not Working

- Verify `NEXTAUTH_SECRET` is set
- Check `NEXTAUTH_URL` matches your domain
- Clear browser cookies and try again

### Gemini AI Not Responding

- Verify `GEMINI_API_KEY` is correct
- Check API quota limits
- Review API usage in Google Cloud Console

## Security Best Practices

1. **Never commit `.env` file** - Already in `.gitignore`
2. **Use strong NEXTAUTH_SECRET** - Generate random string
3. **Hash passwords with bcrypt** - Already implemented
4. **Validate user input** - Use Zod schemas
5. **Limit SQL queries** - Sanitize and validate
6. **Rate limit AI requests** - Implement rate limiting
7. **Use HTTPS in production** - Required for auth cookies

## Performance Optimization

1. **Database Indexes**: Add indexes to frequently queried columns
2. **Query Caching**: Cache expensive queries
3. **Pagination**: Limit results to 50-100 rows
4. **Image Optimization**: Use Next.js Image component
5. **Code Splitting**: Dynamic imports for large components

## Contributing

This is a private project. For questions or issues, contact the development team.

## License

Proprietary - All rights reserved

## Support

For support, email admin@turbo.az or open an issue in the project repository.

---

**Built with ❤️ using Next.js, TypeScript, and Google Gemini AI**
