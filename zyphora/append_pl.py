with open('finance/views.py', 'a', encoding='utf-8') as f:
    f.write('''

# ===============================
# FEATURE 25: P&L ANALYTICS
# ===============================

@login_required(login_url='/users/login')
def project_profit_report(request):
    costings = ProjectCosting.objects.select_related('project').all()
    
    total_revenue = sum(c.selling_price for c in costings)
    total_cost = sum(c.total_cost for c in costings)
    gross_profit = sum(c.gross_margin for c in costings)
    
    avg_margin = 0
    if total_revenue > 0:
        avg_margin = (gross_profit / total_revenue) * 100
        
    context = {
        'costings': costings,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'gross_profit': gross_profit,
        'avg_margin': avg_margin
    }
    return render(request, 'dashboard/finance/pl_dashboard.html', context)
''')
print("Appended P&L view")
