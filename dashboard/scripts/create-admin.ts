/**
 * Create Admin User Script
 *
 * Run this script to create the initial admin user for the dashboard.
 * Usage: npx tsx scripts/create-admin.ts
 */

import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'
import readline from 'readline'

const prisma = new PrismaClient()

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
})

function question(prompt: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(prompt, resolve)
  })
}

async function createAdmin() {
  console.log('\n===========================================')
  console.log('  Create Admin User for Turbo Dashboard')
  console.log('===========================================\n')

  try {
    // Get admin details
    const email = await question('Enter admin email: ')
    const password = await question('Enter admin password: ')
    const confirmPassword = await question('Confirm password: ')

    // Validate input
    if (!email || !email.includes('@')) {
      console.error('❌ Invalid email address')
      process.exit(1)
    }

    if (!password || password.length < 6) {
      console.error('❌ Password must be at least 6 characters')
      process.exit(1)
    }

    if (password !== confirmPassword) {
      console.error('❌ Passwords do not match')
      process.exit(1)
    }

    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email },
    })

    if (existingUser) {
      console.error(`❌ User with email ${email} already exists`)
      process.exit(1)
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10)

    // Create admin user
    const admin = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        role: 'admin',
      },
    })

    console.log('\n✅ Admin user created successfully!')
    console.log(`   Email: ${admin.email}`)
    console.log(`   Role: ${admin.role}`)
    console.log(`   ID: ${admin.id}`)
    console.log('\nYou can now login to the dashboard at http://localhost:3000/login\n')
  } catch (error) {
    console.error('❌ Error creating admin user:', error)
    process.exit(1)
  } finally {
    rl.close()
    await prisma.$disconnect()
  }
}

// Run the script
createAdmin()
