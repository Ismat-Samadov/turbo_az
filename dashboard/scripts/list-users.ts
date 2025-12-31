/**
 * List All Users Script
 *
 * Run this script to view all users in the database.
 * Usage: npx tsx scripts/list-users.ts
 */

import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function listUsers() {
  console.log('\n===========================================')
  console.log('  All Users in Turbo Dashboard')
  console.log('===========================================\n')

  try {
    const users = await prisma.user.findMany({
      orderBy: { createdAt: 'desc' },
    })

    if (users.length === 0) {
      console.log('No users found.')
      console.log('Create an admin user with: npx tsx scripts/create-admin.ts\n')
      return
    }

    console.log(`Total users: ${users.length}\n`)

    users.forEach((user, index) => {
      console.log(`${index + 1}. ${user.email}`)
      console.log(`   Role: ${user.role}`)
      console.log(`   ID: ${user.id}`)
      console.log(`   Created: ${user.createdAt?.toLocaleString() || 'N/A'}`)
      console.log()
    })
  } catch (error) {
    console.error('❌ Error fetching users:', error)
    process.exit(1)
  } finally {
    await prisma.$disconnect()
  }
}

// Run the script
listUsers()
