# Quick Start Guide - Turbo Dashboard

Get the dashboard running in 5 minutes!

## Prerequisites

- Node.js 18+ installed
- PostgreSQL database (already configured)
- Gemini API key (already configured)

## Step-by-Step Setup

### 1. Install Dependencies

```bash
cd /Users/ismatsamadov/turbo_az/dashboard
npm install
```

This installs all required packages (~2-3 minutes).

### 2. Generate Prisma Client

```bash
npx prisma generate
```

Generates the database client based on your schema.

### 3. Create Users Table

```bash
npx prisma db push
```

Creates the `users` table in your existing database (won't affect `scraping.turbo_az` table).

### 4. Create Admin User

Open your PostgreSQL client and run:

```sql
INSERT INTO users (id, email, password, name, role, created_at, updated_at)
VALUES (
  'admin-001',
  'admin@turbo.az',
  '$2a$10$K7L/SbSKEQBZe.Qlg4bXa.qRhJgF1gy0/z7nQ7j6nJ0wQY7JLjVPS',
  'Admin User',
  'admin',
  NOW(),
  NOW()
);
```

**Login credentials**:
- Email: `admin@turbo.az`
- Password: `admin123`

### 5. Start Development Server

```bash
npm run dev
```

Dashboard will start at: **http://localhost:3000**

---

## Testing the Dashboard

### 1. Test Landing Page
✅ Open http://localhost:3000
✅ You should see the professional landing page

### 2. Test Login
✅ Click "Get Started" or go to http://localhost:3000/login
✅ Login with `admin@turbo.az` / `admin123`
✅ You should be redirected to `/dashboard`

### 3. Test AI Queries
✅ In the dashboard, type: "How many cars are there?"
✅ Click "Ask"
✅ You should see:
   - Generated SQL query
   - Query results in a table
   - AI explanation

### 4. Test Admin Panel
✅ Click "Admin Panel" button (visible to admins)
✅ You should see the user list
✅ Try creating a new user via registration page

---

## Example AI Questions

Try these in the dashboard:

```
How many total car listings are there?
```

```
What are the top 5 most popular car makes?
```

```
Show me average year by make (top 10)
```

```
How many listings are in Bakı?
```

```
What percentage of cars are automatic transmission?
```

---

## Common Issues

### Issue: `npm install` fails
**Solution**: Make sure you're in the `/dashboard` directory

### Issue: Prisma errors
**Solution**: Run `npx prisma generate` again

### Issue: Can't login
**Solution**:
1. Make sure you ran the SQL to create admin user
2. Clear browser cookies
3. Restart dev server

### Issue: AI queries not working
**Solution**: Check `.env` file has correct `GEMINI_API_KEY`

### Issue: Database connection failed
**Solution**: Check `DATABASE_URL` in `.env` matches your PostgreSQL connection

---

## File Structure (Important Files)

```
dashboard/
├── .env                  ← Environment variables (check this!)
├── package.json          ← Dependencies
├── prisma/schema.prisma  ← Database schema
├── app/
│   ├── page.tsx         ← Landing page
│   ├── (auth)/login/    ← Login page
│   ├── (dashboard)/
│   │   ├── dashboard/   ← Main dashboard (AI queries)
│   │   └── admin/       ← Admin panel
│   └── api/
│       ├── ai/query/    ← AI endpoint
│       └── users/       ← User management
└── lib/
    ├── gemini.ts        ← AI integration
    └── auth.ts          ← Authentication config
```

---

## Environment Variables

Check your `.env` file contains:

```env
# Database (same as scraper)
DATABASE_URL="postgresql://myfrog_me_owner:ErAVlQSW06Ih@ep-red-dew-a22obfoo.eu-central-1.aws.neon.tech/myfrog_me?sslmode=require"

# NextAuth
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-change-this-in-production"

# Gemini AI
GEMINI_API_KEY="AIzaSyCjzRCVEKUrWoLwzFwa1YoBekcplh8rHLs"
```

---

## Next Steps

Once everything works:

1. **Create Regular Users**: Test registration at `/register`
2. **Explore AI Queries**: Try different questions
3. **Check Admin Panel**: Manage users
4. **Customize**: Modify pages to fit your needs
5. **Deploy**: Deploy to Vercel or your preferred platform

---

## Production Deployment

### Deploy to Vercel

1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "Add dashboard"
   git push
   ```

2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Add environment variables:
   - `DATABASE_URL`
   - `NEXTAUTH_URL` (your production URL)
   - `NEXTAUTH_SECRET` (generate new one: `openssl rand -base64 32`)
   - `GEMINI_API_KEY`
5. Deploy!

---

## Support

- **Full Documentation**: See `README.md` and `FINAL_SETUP.md`
- **Project Overview**: See `/PROJECT_COMPLETE.md` in root directory
- **Database Schema**: See `prisma/schema.prisma`

---

## Quick Commands Reference

```bash
# Install
npm install

# Development
npm run dev

# Build for production
npm run build
npm start

# Database
npx prisma studio      # Open database GUI
npx prisma generate    # Regenerate Prisma client
npx prisma db push     # Push schema changes
```

---

**That's it! You're ready to go! 🚀**

Dashboard: http://localhost:3000
Login: `admin@turbo.az` / `admin123`

Enjoy analyzing 13,000+ car listings with AI! 🚗✨
