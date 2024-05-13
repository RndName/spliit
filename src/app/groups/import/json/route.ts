import { getPrisma } from '@/lib/prisma'
import { Prisma } from '@prisma/client'
import { randomId, getCategories } from '@/lib/api'

export async function POST(req: Request){
    const res = await req.json() as any
    const prisma = await getPrisma()

    //TODO Failsafe

    // Get map of category name to ID
    const categoryMapping: Record<string, number> = {}
    const categories = await getCategories()

    for (const categoryRow of categories) {
        categoryMapping[categoryRow.name] = categoryRow.id
    }

    const groupId = randomId()
    const group: Prisma.GroupCreateInput = {
        id: groupId,
        name: res.name,
        currency: res.currency,
        createdAt: new Date(),
      }

    
    const participantIdsMapping: Record<string, string> = {}
    const participants: Prisma.ParticipantCreateManyInput[] = []

    for (const participant of res.participants) {
        const id = randomId()
        participantIdsMapping[participant.id] = id
        participants.push({
            id,
            groupId: groupId,
            name: participant.name,
        })
    }

    const expenses: Prisma.ExpenseCreateManyInput[] = []
    const expenseParticipants: Prisma.ExpensePaidForCreateManyInput[] = []  

    for (const expense of res.expenses) {

        const expenseId = randomId()

        expenses.push({
            id: expenseId,
            amount: expense.amount,
            groupId: groupId,
            title: expense.title,
            expenseDate: new Date(expense.expenseDate),
            categoryId: categoryMapping[expense.category.name],
            createdAt: new Date(),
            isReimbursement: expense.isReimbursement,
            paidById: participantIdsMapping[expense.paidById],
            splitMode: expense.splitMode
          })

        for (const expenseParticipant of expense.paidFor){
            expenseParticipants.push({
                expenseId: expenseId,
                participantId: participantIdsMapping[expenseParticipant.participantId],
                shares: expenseParticipant.shares
              })
        }
    }

    console.log('Creating group:', group)
    await prisma.group.create({ data: group })

    console.log('Creating participants:', participants)
    await prisma.participant.createMany({ data: participants })

    console.log('Creating expenses:', expenses)
    await prisma.expense.createMany({ data: expenses })

    console.log('Creating expenseParticipants:', expenseParticipants)
    await prisma.expensePaidFor.createMany({data: expenseParticipants })

    console.log(groupId)

    return Response.json({ group })

}