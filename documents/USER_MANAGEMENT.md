# User Management Guide

This guide explains how to manage users in the Turbo Dashboard.

## Table of Contents
- [Initial Setup](#initial-setup)
- [Creating the First Admin](#creating-the-first-admin)
- [Managing Users](#managing-users)
- [User Roles](#user-roles)
- [Security Best Practices](#security-best-practices)

---

## Initial Setup

### Database Schema

The dashboard uses a `users` table in PostgreSQL with the following structure:

```sql
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT DEFAULT 'user' NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Prisma Schema

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  password  String
  role      String   @default("user")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  @@map("users")
}
```

---

## Creating the First Admin

**IMPORTANT**: Before you can use the dashboard, you must create an initial admin user.

### Method 1: Using the Script (Recommended)

```bash
cd dashboard
npm run create-admin
```

You'll be prompted to enter:
- Email address
- Password (minimum 6 characters)
- Password confirmation

Example:
```
===========================================
  Create Admin User for Turbo Dashboard
===========================================

Enter admin email: admin@turbo.az
Enter admin password: ••••••••
Confirm password: ••••••••

✅ Admin user created successfully!
   Email: admin@turbo.az
   Role: admin
   ID: clq1a2b3c4d5e6f7g8h9i0j

You can now login to the dashboard at http://localhost:3000/login
```

### Method 2: Using Direct SQL

If you prefer, you can create an admin user directly in the database:

```sql
-- Generate a bcrypt hash for your password first (use bcryptjs or online tool)
-- Example hash for password "admin123": $2a$10$YourHashHere

INSERT INTO users (id, email, password, role)
VALUES (
  gen_random_uuid()::text,
  'admin@turbo.az',
  '$2a$10$YourBcryptHashHere',  -- Replace with actual bcrypt hash
  'admin'
);
```

---

## Managing Users

### Viewing All Users

List all users in the database:

```bash
cd dashboard
npm run list-users
```

Output:
```
===========================================
  All Users in Turbo Dashboard
===========================================

Total users: 3

1. admin@turbo.az
   Role: admin
   ID: clq1a2b3c4d5e6f7g8h9i0j
   Created: 12/31/2025, 10:00:00 AM

2. user1@company.com
   Role: user
   ID: clq2b3c4d5e6f7g8h9i0j1k
   Created: 12/31/2025, 11:00:00 AM

3. analyst@company.com
   Role: user
   ID: clq3c4d5e6f7g8h9i0j1k2l
   Created: 12/31/2025, 12:00:00 PM
```

### Creating Users via Admin Panel

1. **Login as Admin**
   - Go to `http://localhost:3000/login`
   - Enter admin credentials
   - Click "Sign In"

2. **Access Admin Panel**
   - Click "Admin Panel" button in the header
   - Or navigate to `http://localhost:3000/admin`

3. **Create New User**
   - Click "Add New User" button
   - Fill in the form:
     - Email: User's email address
     - Password: Temporary password (user should change it later)
     - Role: Select "user" or "admin"
   - Click "Create User"

4. **View All Users**
   - Admin panel shows all users in a table
   - Each row displays: Email, Role, Created date

5. **Delete User**
   - Click the "Delete" button next to the user
   - Confirm deletion in the dialog
   - **Note**: You cannot delete your own account while logged in

---

## User Roles

### Admin Role
**Permissions:**
- Full access to all features
- Can access admin panel (`/admin`)
- Can create new users (admin or regular)
- Can delete other users
- Can view all dashboard analytics
- Can execute AI queries

**Use Cases:**
- System administrators
- Business owners
- Data analysts who need to manage team access

### User Role
**Permissions:**
- Can access main dashboard (`/dashboard`)
- Can view all analytics and charts
- Can execute AI queries
- Cannot access admin panel
- Cannot manage other users

**Use Cases:**
- Team members
- Analysts
- Stakeholders who need read-only access

---

## Security Best Practices

### Password Requirements
- Minimum 6 characters (enforced by the create-admin script)
- Recommend: At least 12 characters with mixed case, numbers, and symbols
- Passwords are hashed using bcrypt with salt rounds = 10

### Admin Account Security
1. **Use Strong Passwords**
   - Don't use common passwords
   - Use a password manager
   - Change passwords regularly

2. **Limit Admin Accounts**
   - Only create admin accounts for trusted personnel
   - Use regular "user" role for most team members

3. **Environment Variables**
   - Never commit `.env` files to git
   - Use strong `NEXTAUTH_SECRET` (32+ random characters)
   - Store credentials securely

### Session Security
- Sessions use JWT with NextAuth.js v5
- Sessions expire after inactivity
- Secure cookies in production (HTTPS only)

---

## Troubleshooting

### Cannot Login

**Issue**: "Invalid credentials" error

**Solutions**:
1. Verify email is correct (case-sensitive)
2. Check password (ensure no extra spaces)
3. Verify user exists: `npm run list-users`
4. Check database connection in `.env`

### Cannot Access Admin Panel

**Issue**: Redirected to dashboard when accessing `/admin`

**Solutions**:
1. Verify you're logged in as admin
2. Check user role in database:
   ```sql
   SELECT email, role FROM users WHERE email = 'your@email.com';
   ```
3. If role is "user", update to "admin":
   ```sql
   UPDATE users SET role = 'admin' WHERE email = 'your@email.com';
   ```

### Password Reset

Currently, password reset must be done manually:

```sql
-- Generate new bcrypt hash for new password
UPDATE users
SET password = '$2a$10$NewBcryptHashHere'
WHERE email = 'user@email.com';
```

**Future Feature**: Self-service password reset via email

---

## Database Queries

### Useful SQL Queries

**Count users by role:**
```sql
SELECT role, COUNT(*) as count
FROM users
GROUP BY role;
```

**Find all admin users:**
```sql
SELECT email, created_at
FROM users
WHERE role = 'admin'
ORDER BY created_at DESC;
```

**Delete a user:**
```sql
DELETE FROM users WHERE email = 'user@email.com';
```

**Change user role:**
```sql
UPDATE users
SET role = 'admin'
WHERE email = 'user@email.com';
```

**View recent users:**
```sql
SELECT email, role, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
```

---

## Workflow Example

### Onboarding a New Team Member

1. **Admin creates account**
   ```bash
   # Admin logs into dashboard
   # Goes to Admin Panel
   # Clicks "Add New User"
   # Email: newuser@company.com
   # Password: TempPass123!
   # Role: user
   # Clicks "Create User"
   ```

2. **Share credentials securely**
   - Send email/password via secure channel
   - Don't send both in same message
   - Recommend immediate password change

3. **User logs in**
   - User navigates to `/login`
   - Enters credentials
   - Accesses dashboard

4. **Optional: Promote to admin**
   - If user needs admin access later
   - Admin can update role via SQL or by deleting/recreating

---

## API Integration

### Programmatic User Creation

For automated user creation, you can use the Prisma client:

```typescript
import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function createUser(email: string, password: string, role: 'admin' | 'user') {
  const hashedPassword = await bcrypt.hash(password, 10)

  const user = await prisma.user.create({
    data: {
      email,
      password: hashedPassword,
      role,
    },
  })

  return user
}
```

---

## Next Steps

- **Implement Password Reset**: Add self-service password reset via email
- **Two-Factor Authentication**: Add 2FA for admin accounts
- **Audit Logging**: Track user actions (login, user creation, deletion)
- **Bulk User Import**: CSV upload for creating multiple users
- **User Profiles**: Extended user information (name, department, etc.)

---

**Last Updated**: 2025-12-31
**Version**: 1.0.0
