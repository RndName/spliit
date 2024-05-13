import csv
import json
from json import JSONEncoder

class Participant:
    def __init__(self, name):
        self.id = name
        self.name = name

class Group:
    def __init__(self):
        self.name: str = ""
        self.participants: list[str] = []
        self.currency: str = "€"
        self.expenses: list[str] = []
    
class Category:
    def __init__(self):
        self.name = "General"

class ExpensePaidFor:
    def __init__(self):
        self.participantId: str = ""
        self.shares: int = 1
    
class Expense:
    def __init__(self):
        self.expenseDate: str = ""
        self.title: str = ""
        self.amount: int = 0
        self.category: Category = Category()
        self.paidById: str = ""
        self.paidFor: list[ExpensePaidFor]= []
        self.isReimbursement: bool = False
        self.splitMode: str =  "BY_PERCENTAGE"
    
class GroupEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
    
projects = ["haushalt", "lanzarote", "urlaub_alt", "muenchen"]   
    
def migrate(projectName) -> None:
    group: Group = Group()
    group.name = projectName
    participants: dict(str, str) = {}
    with open(projectName + ".CSV", newline='') as csvfile:
        expenses = []
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for idx, row in enumerate(spamreader):
            if idx==0:
                continue
            expense: Expense = Expense()
            expense.title = row[0]
            expense.expenseDate = row[2] + "T00:00:00.000Z"
            expense.amount = int(float(row[1])*100)
            expense.paidById = row[4]
            if row[4] not in participants:
                participants[row[4]] = row[4]
            owerlist = []
            owers = row[7].split(",")
            for ower in owers:
                expensePaidfor: ExpensePaidFor = ExpensePaidFor()
                expensePaidfor.participantId = ower
                if (len(owers) == 1) or (row[5] == "1"):
                    expense.splitMode = "EVENLY"
                elif ower == expense.paidById:
                    expensePaidfor.shares = int(float(row[5])*100*100)
                else:
                    expensePaidfor.shares = int((1-float(row[5]))*100*100)
                owerlist.append(expensePaidfor)
                if ower not in participants:
                    participants[ower] = ower
            expense.paidFor = owerlist
            expenses.append(expense)
    group.expenses = expenses
    
    participantList= []
    for p in participants.values():
        participantList.append(Participant(p))
    group.participants = participantList
    
    with open(projectName + ".json", 'w', encoding='utf8') as f:
        json.dump(group, f, indent=4, cls=GroupEncoder, ensure_ascii=False)

for project in projects:
    migrate(project)
        
    