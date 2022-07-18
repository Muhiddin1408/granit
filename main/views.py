from datetime import timedelta
from django.db.models import FloatField, IntegerField
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum, F
from django.views.generic import TemplateView
from api.models import *
from django.db.models import Q
from datetime import date, datetime
from django.http.response import JsonResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
# SMS
from django.conf import settings
from .sms_sender import sendSmsOneContact
import xlrd
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .forms import AddFilialForm
from django.db.models.functions import Coalesce
import json
# import datetime
from django.core.paginator import Paginator


def monthly():
    date = datetime.today()
    year = date.year
    if date.month == 12:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year, date.month + 1, 1, 0, 0, 0)

    return gte, lte


def ChartHome(request):
    kirims = []
    kirimd = []
    chiqims = []
    chiqimd = []
    for i in range(1, 13):
        date = datetime.today()
        year = date.year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        gte = str(year) + '-' + str(i) + '-01 00:01:00'
        lte = str(year2) + '-' + str(month2) + '-01 00:01:00'
        gte_without_time = str(year) + '-' + str(i) + '-01'
        lte_without_time = str(year2) + '-' + str(month2) + '-01'
        kirr = CashboxReceive.objects.filter(
            status="accepted", date__range=(gte_without_time, lte_without_time))
        ks = 0
        kd = 0
        for kir in kirr:
            kd += kir.total_sum
        chs = 0
        chd = 0
        chiqq = Chiqim.objects.filter(qachon__gte=gte, qachon__lte=lte)
        for chiq in chiqq:
            chs += chiq.qancha_som
            chd += chiq.qancha_dol
        kirims.append(ks)
        kirimd.append(kd)
        chiqims.append(chs)
        chiqimd.append(chd)

    total_income = sum(kirimd)
    total_expense = sum(chiqimd)

    dt = {
        'kirimd': kirimd,
        'chiqimd': chiqimd,
        'total_income': total_income,
        'total_expense': total_expense
    }
    return JsonResponse(dt)


def FilialKirim(request):
    year = datetime.today().year
    filials = Filial.objects.all()

    response = []
    for filial in filials:
        response.append({"name": f"{filial}", "data": [
            round(Shop.objects.filter(filial=filial, date__year=year, date__month=i).aggregate(foo=Coalesce(
                Sum(F('naqd_dollar') + F('plastik') + F('transfer') + F('nasiya_dollar') - F('skidka_dollar')),
                0
            ))['foo'], 2) for i in range(1, 13)]})

    return JsonResponse({"response": response})


def SalerKirim(request):
    saler1 = []
    saler2 = []
    saler3 = []
    for i in range(1, 13):
        date = datetime.today()
        year = date.year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        gte = str(year) + '-' + str(i) + '-01 00:01:00'
        lte = str(year2) + '-' + str(month2) + '-01 00:01:00'
        a = Shop.objects.filter(date__gte=gte, date__lte=lte).values('saler').annotate(
            som=Sum('naqd_som') + Sum('plastik') + Sum('nasiya_som') +
                Sum('transfer') + Sum('skidka_som'),
            dollar=Sum('naqd_dollar') + Sum('nasiya_dollar') + Sum('skidka_dollar'))
        # try:
        #     saler1.append(a[0]['num'])
        # except:
        #     saler1.append('0')
        # try:
        #     saler2.append(a[1]['num'])
        # except:
        #     saler2.append('0')
        # try:
        #     saler3.append(a[2]['num'])
        # except:
        #     saler3.append('0')
        print(a)
    # print(fil1, fil2, fil3)
    dt = {
        'saler1': saler1,
        'saler2': saler2,
        'saler3': saler3,
    }
    return JsonResponse(dt)


def Summa(request):
    gte, lte = monthly()
    shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
    naqd_som = 0
    naqd_dollar = 0
    plastik = 0
    nasiya_som = 0
    nasiya_dollar = 0
    transfer = 0
    skidka_som = 0
    skidka_dollar = 0
    for shop in shops:
        naqd_som += shop.naqd_som
        naqd_dollar += shop.naqd_dollar
        plastik += shop.plastik
        nasiya_som += shop.nasiya_som
        nasiya_dollar += shop.nasiya_dollar
        transfer += shop.transfer
        skidka_som += shop.skidka_som
        skidka_dollar += shop.skidka_dollar
    som = naqd_som + plastik + nasiya_som + transfer + skidka_som
    dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

    dt = {
        'naqd_som': int(naqd_som),
        'naqd_dollar': int(naqd_dollar),
        'plastik': int(plastik),
        'nasiya_som': nasiya_som,
        'nasiya_dollar': int(nasiya_dollar),
        'transfer': int(transfer),
        'skidka_som': skidka_som,
        'skidka_dollar': int(skidka_dollar),
        'som': som,
        'dollar': int(dollar),
    }
    return JsonResponse(dt)


# def Qoldiq(request):
#     fil = Filial.objects.extra(
#         select = {
#             'som':'select sum(api_productfilial.som * api_productfilial.quantity) from api_productfilial where api_productfilial.filial_id = api_filial.id',
#             'dollar':'select sum(api_productfilial.dollar * api_productfilial.quantity) from api_productfilial where api_productfilial.filial_id = api_filial.id'
#         }
#     )
#     fils = []
#     for f in fil:
#         fils.append(f.name)
#     filq = []
#     nol = 0
#     for f in fil:
#         if f.som:
#             filq.append(f.som)
#             filq.append(f.dollar)
#         else:
#             filq.append(nol)
#             filq.append(nol)
#     dt = {
#         'qoldiq':filq,
#         'filial':fils
#     }
#     return JsonResponse(dt)

def DataHome(request):
    data = json.loads(request.body)
    gte = data['date1']
    lte = data['date2']
    print(gte, lte)
    salers = UserProfile.objects.extra(
        select={
            'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
        }
    )

    # Saler nasiya foizni hisoblash uchun
    for s in salers:
        print(s.nasiya_dollar)
        s.nasiya_foiz = 0
        if s.naqd_dollar is not None:
            s.nasiya_foiz += s.naqd_dollar
        if s.plastik is not None:
            s.nasiya_foiz += s.plastik
        if s.nasiya_dollar is not None:
            s.nasiya_foiz += s.nasiya_dollar
        if s.transfer is not None:
            s.nasiya_foiz += s.transfer
        if s.skidka_dollar is not None:
            s.nasiya_foiz -= s.skidka_dollar
        foo = s.nasiya_foiz / 100
        s.nasiya_foiz = s.nasiya_dollar / foo if s.nasiya_dollar is not None else 0
        s.save()

    filials = Filial.objects.extra(
        select={
            'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                gte, lte),
            'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                gte, lte)
        }
    )

    # Filial nasiya foizni hisoblash uchun
    for f in filials:
        f.nasiya_foiz = 0
        if f.naqd_dollar:
            f.nasiya_foiz += f.naqd_dollar
        if f.plastik:
            f.nasiya_foiz += f.plastik
        if f.nasiya_dollar:
            f.nasiya_foiz += f.nasiya_dollar
        if f.transfer:
            f.nasiya_foiz += f.transfer
        foo = f.nasiya_foiz / 100
        f.nasiya_foiz = f.nasiya_dollar / foo if f.nasiya_dollar else 0
        f.save()

    shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
    naqd_som = 0
    naqd_dollar = 0
    plastik = 0
    nasiya_som = 0
    nasiya_dollar = 0
    transfer = 0
    skidka_som = 0
    skidka_dollar = 0
    for shop in shops:
        naqd_som += shop.naqd_som
        naqd_dollar += shop.naqd_dollar
        plastik += shop.plastik
        nasiya_som += shop.nasiya_som
        nasiya_dollar += shop.nasiya_dollar
        transfer += shop.transfer
        skidka_som += shop.skidka_som
        skidka_dollar += shop.skidka_dollar
    som = naqd_som + plastik + nasiya_som + transfer + skidka_som
    dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

    if som >= 0:
        se = []
        for saler in salers:
            s = {
                'name': saler.first_name,
                'staff': saler.staff,
                'filial': saler.filial.name,
                'naqd_som': saler.naqd_som,
                'naqd_dollar': saler.naqd_dollar,
                'plastik': saler.plastik,
                'nasiya_som': saler.nasiya_som,
                'nasiya_dollar': saler.nasiya_dollar,
                'transfer': saler.transfer,
                'skidka_som': saler.skidka_som,
                'skidka_dollar': saler.skidka_dollar,
                'nasiya_foiz': saler.nasiya_foiz
            }
            se.append(s)
        fl = []
        for filial in filials:
            t = {
                'name': filial.name,
                'naqd_som': filial.naqd_som,
                'naqd_dollar': filial.naqd_dollar,
                'plastik': filial.plastik,
                'nasiya_som': filial.nasiya_som,
                'nasiya_dollar': filial.nasiya_dollar,
                'transfer': filial.transfer,
                'skidka_som': filial.skidka_som,
                'skidka_dollar': filial.skidka_dollar,
                'nasiya_foiz': filial.nasiya_foiz,
                'pay_dollar': filial.pay_dollar
            }
            fl.append(t)
        dt1 = {
            'salers': se,
            'filials': fl,
            'naqd_som': naqd_som,
            'naqd_dollar': naqd_dollar,
            'plastik': plastik,
            'nasiya_som': nasiya_som,
            'nasiya_dollar': nasiya_dollar,
            'transfer': transfer,
            'skidka_som': skidka_som,
            'skidka_dollar': skidka_dollar,
        }
    else:
        se = []
        for saler in salers:
            s = {
                'name': saler.first_name,
                'staff': saler.staff,
                'filial': saler.filial.name,
                'naqd_som': 0,
                'naqd_dollar': 0,
                'plastik': 0,
                'nasiya_som': 0,
                'nasiya_dollar': 0,
                'transfer': 0,
                'skidka_som': 0,
                'skidka_dollar': 0,
                'nasiya_foiz': 0,
            }
            se.append(s)
        fl = []
        for filial in filials:
            t = {
                'name': filial.name,
                'naqd_som': 0,
                'naqd_dollar': 0,
                'plastik': 0,
                'nasiya_som': 0,
                'nasiya_dollar': 0,
                'transfer': 0,
                'skidka_som': 0,
                'skidka_dollar': 0,
                'nasiya_foiz': 0
            }
            fl.append(t)

        dt1 = {
            'salers': se,
            'filials': fl,
            'naqd_som': 0,
            'naqd_dollar': 0,
            'plastik': 0,
            'nasiya_som': 0,
            'nasiya_dollar': 0,
            'transfer': 0,
            'skidka_som': 0,
            'skidka_dollar': 0,
        }
    return JsonResponse(dt1)


def DataWare(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    wares = Receive.objects.filter(date__gte=date1, date__lte=date2)
    wr = []
    for w in wares:
        t = {
            'id': w.id,
            'deliver': w.deliver.name,
            'name': w.name,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M")

        }
        wr.append(t)
    dt1 = {
        'wares': wr
    }
    return JsonResponse(dt1)


def DebtorHistory(request):
    gte, lte = monthly()
    d_id = request.GET.get('d')
    pays = PayHistory.objects.filter(
        date__gte=gte, date__lte=lte, debtor_id=d_id)
    debts = Debt.objects.filter(date__gte=gte, date__lte=lte, debtor_id=d_id)
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        pdollar += p.dollar
    for d in debts:
        dsom += d.som
        ddollar += d.dollar

    context = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': dsom,
        'ddollar': ddollar,
        'pays': pays,
        'debts': debts,
        'd_id': d_id,
        'debtor': "active",
        'debtor_t': "true"
    }

    return render(request, 'debtorhistory.html', context)


def filialinfo(request, id):
    filial = Filial.objects.get(id=id)
    shops = Shop.objects.filter(filial=filial)
    incomes = CashboxReceive.objects.filter(filial=filial).order_by('-id')

    date1 = request.GET.get('date1')
    date2 = request.GET.get('date2')
    if date1 and date2:
        shops = shops.filter(date__range=(date1, date2))
        incomes = incomes.filter(date__range=(date1, date2))

    total_income = incomes.filter(status='accepted').aggregate(
        foo=Sum("total_sum"))['foo']
    total_shop = shops.all().aggregate(foo=Sum(
        F("naqd_dollar") + F("transfer") + F("plastik") +
        F("nasiya_dollar") - F("skidka_dollar")
    ))['foo']
    if total_income is None:
        total_income = 0
    if total_shop is None:
        total_shop = 0
    farq = total_shop - total_income

    context = {
        'fil': filial,
        'filial': "active",
        'filial_t': "true",
        'incomes': incomes,
        'total_income': total_income,
        'total_shop': total_shop,
        'farq': farq
    }

    return render(request, 'filialinfo.html', context)


def DeliverHistory(request):
    gte, lte = monthly()
    d_id = request.GET.get('d')
    pays = DeliverPayHistory.objects.filter(
        date__gte=gte, date__lte=lte, deliver_id=d_id)
    debts = DebtDeliver.objects.filter(
        date__gte=gte, date__lte=lte, deliver_id=d_id)
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        pdollar += p.dollar
    for d in debts:
        dsom += d.som
        ddollar += d.dollar

    context = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': dsom,
        'ddollar': ddollar,
        'pays': pays,
        'debts': debts,
        'd_id': d_id,
        'deliver': "active",
        'deliver_t': "true"
    }

    return render(request, 'deliverhistory.html', context)


def NasiyaTarix(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    d_id = data['d_id']
    # print(date1, date2, d_id)
    pays = PayHistory.objects.filter(
        date__gte=date1, date__lte=date2, debtor_id=d_id)
    debts = Debt.objects.filter(
        date__gte=date1, date__lte=date2, debtor_id=d_id)
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        pdollar += p.dollar
    for d in debts:
        dsom += d.som
        ddollar += d.dollar
    pay = []
    for w in pays:
        print("p")
        t = {
            # 'id': w.id,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M"),
        }
        pay.append(t)
    debt = []
    for w in debts:
        print("d")
        t = {
            # 'id': w.id,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date,
        }
        debt.append(t)
    dt1 = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': dsom,
        'ddollar': ddollar,
        'pays': pay,
        'debts': debt,
    }
    return JsonResponse(dt1)


def kurs_page(request):
    if request.method == 'POST':
        kurs = request.POST.get('kurs')
        kurs_baza = 0
        try:
            kurs_baza = Exchange.objects.first()
            kurs = float(kurs)
            kurs_baza.kurs = kurs
            kurs_baza.save()
        except:
            pass
        return render(request, 'change_kurs_page.html', {'kurs': kurs_baza})
    else:
        kurs = Exchange.objects.first()
        return render(request, 'change_kurs_page.html', {'kurs': kurs})


def add_tolov(request):
    deliver_id = request.POST.get('deliver_id')
    som = request.POST.get('som')
    izoh = request.POST.get('izoh')
    dollor = request.POST.get('dollor')
    turi = request.POST.get('turi')
    ht = DeliverPayHistory.objects.create(
        deliver_id=deliver_id, som=som, dollar=dollor, turi=turi, izoh=izoh)

    url = "/deliverhistory/?d=" + str(deliver_id)
    return redirect(url)


def GetItem(request):
    data = json.loads(request.body)
    id = data['id']
    items = ReceiveItem.objects.filter(receive_id=id)
    it = []
    for i in items:
        its = {
            'id': i.id,
            'product': i.product.name,
            'som': i.som,
            'dollar': i.dollar,
            'kurs': i.kurs,
            'quantity': i.quantity
        }
        it.append(its)
    dt1 = {
        'items': it
    }
    return JsonResponse(dt1)


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):

        today = date.today()
        gte = datetime(today.year, today.month, today.day, 0, 0, 0)
        lte = datetime(today.year, today.month, today.day, 23, 59, 59)

        salers = UserProfile.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
            }
        )
        filials = Filial.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte),
                'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte),
            }
        )
        # Filial nasiya foizni hisoblash uchun
        for f in filials:
            f.nasiya_foiz = 0
            if f.nasiya_dollar is not None:
                if f.nasiya_dollar > 0:
                    if f.naqd_dollar is not None:
                        f.nasiya_foiz += f.naqd_dollar
                    if f.plastik is not None:
                        f.nasiya_foiz += f.plastik
                    if f.nasiya_dollar is not None:
                        f.nasiya_foiz += f.nasiya_dollar
                    if f.transfer is not None:
                        f.nasiya_foiz += f.transfer
                    foo = f.nasiya_foiz / 100
                    f.nasiya_foiz = f.nasiya_dollar / foo if f.nasiya_dollar is not None else 0
            f.save()

        # Saler nasiya foizni hisoblash uchun
        for s in salers:
            s.nasiya_foiz = 0
            if s.nasiya_dollar is not None:
                if s.nasiya_dollar > 0:
                    if s.naqd_dollar is not None:
                        s.nasiya_foiz += s.naqd_dollar
                    if s.plastik is not None:
                        s.nasiya_foiz += s.plastik
                    if s.nasiya_dollar is not None:
                        s.nasiya_foiz += s.nasiya_dollar
                    if s.transfer is not None:
                        s.nasiya_foiz += s.transfer
                    if s.skidka_dollar is not None:
                        s.nasiya_foiz -= s.skidka_dollar
                    foo = s.nasiya_foiz / 100
                    s.nasiya_foiz = s.nasiya_dollar / foo if s.nasiya_dollar is not None else 0
            s.save()

        shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
        naqd_som = 0
        naqd_dollar = 0
        plastik = 0
        nasiya_som = 0
        nasiya_dollar = 0
        transfer = 0
        skidka_som = 0
        skidka_dollar = 0
        for shop in shops:
            naqd_som = naqd_som + shop.naqd_som
            naqd_dollar = naqd_dollar + shop.naqd_dollar
            plastik = plastik + shop.plastik
            nasiya_som = nasiya_som + shop.nasiya_som
            nasiya_dollar = nasiya_dollar + shop.nasiya_dollar
            transfer = transfer + shop.transfer
            skidka_som = skidka_som + shop.skidka_som
            skidka_dollar = skidka_dollar + shop.skidka_dollar
        som = naqd_som + nasiya_som + skidka_som
        dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

        jami = float(shops.aggregate(foo=Coalesce(
            Sum(F('naqd_dollar') + F('plastik') + F('nasiya_dollar') +
                F('transfer') - F('skidka_dollar')),
            0
        ))['foo'])

        total_income = CashboxReceive.objects.filter(status="accepted", currency='dollar').aggregate(foo=Coalesce(
            Sum('total_sum'),
            0.00
        ))['foo']
        total_income_som = CashboxReceive.objects.filter(status="accepted", currency="so'm").aggregate(foo=Coalesce(
            Sum('total_sum'),
            0.00
        ))['foo']
        total_income_carta = CashboxReceive.objects.filter(status="accepted", currency="carta").aggregate(foo=Coalesce(
            Sum('total_sum'),
            0.00
        ))['foo']
        total_income_utkazma = \
            CashboxReceive.objects.filter(status="accepted", currency="utkazma").aggregate(foo=Coalesce(
                Sum('total_sum'),
                0.00
            ))['foo']

        total_expense = Chiqim.objects.aggregate(foo=Coalesce(
            Sum('qancha_dol'),
            0.00
        ))['foo']
        total_expense_som = Chiqim.objects.aggregate(foo=Coalesce(
            Sum('qancha_som'),
            0.00
        ))['foo']
        total_expense_utkazma = Chiqim.objects.aggregate(foo=Coalesce(
            Sum('qancha_hisob_raqamdan'),
            0.00
        ))['foo']

        context = super().get_context_data(**kwargs)
        context['total_income'] = total_income
        context['total_income_som'] = total_income_som
        context['total_income_carta'] = total_income_carta
        context['total_income_utkazma'] = total_income_utkazma
        context['total_expense'] = total_expense
        context['total_expense_som'] = total_expense_som
        context['total_expense_utkazma'] = total_expense_utkazma
        context['home'] = 'active'
        context['home_t'] = 'true'
        context['salers'] = salers
        context['filials'] = filials
        context['jami'] = jami

        context['naqd_som'] = naqd_som
        context['naqd_dollar'] = naqd_dollar
        context['plastik'] = plastik
        context['nasiya_som'] = nasiya_som
        context['nasiya_dollar'] = nasiya_dollar
        context['transfer'] = transfer
        context['skidka_som'] = skidka_som
        context['skidka_dollar'] = skidka_dollar
        return context


class LTV(LoginRequiredMixin, TemplateView):
    template_name = 'LTV.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ltv'] = 'active'
        context['ltv_t'] = 'true'

        return context


# get ajax LTV datas


def get_ltv_data(request):
    try:
        # time
        day = datetime.now()
        month = day.month
        year = day.year

        date_start = request.GET.get('start')
        date_end = request.GET.get('end')

        if month == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = month + 1
            year2 = year
        gte = datetime(year, month, 1)
        lte = datetime(year2, month2, 1)

        ll = []
        if date_start is not None and date_end is not None:
            debrors = Debtor.objects.filter(
                date__gte=date_start, date__lte=date_end)
            debtor_pay_history = PayHistory.objects.filter(
                date__gte=date_start, date__lte=date_end)
        else:
            debrors = Debtor.objects.filter(date__month=month)
            debtor_pay_history = PayHistory.objects.filter(date__month=month)
        productfilials = ProductFilial.objects.all()
        all_clint_qarz_som = 0
        all_clint_qarz_dollar = 0
        all_clint_tulagan_som = 0
        all_clint_tulagan_dollar = 0
        all_clint_qarz_qoldiq_som = 0
        all_clint_qarz_qoldiq_dollar = 0
        all_clint_daromad_som = 0
        all_clint_daromad_dollar = 0
        for debror in debrors:
            # qarz
            qarz_sum = debrors.filter(id=debror.id, ).aggregate(
                Sum('som'))['som__sum']
            qarz_dollar = debrors.filter(id=debror.id).aggregate(
                Sum('dollar'))['dollar__sum']

            # mijoz olgan avarlar total sotish summasi
            total_olgan_tavar_sum = productfilials.filter(
                filial__filial_pay__debtor_id=debror.id).aggregate(Sum('sotish_som'))['sotish_som__sum']
            total_olgan_tavar_dollar = productfilials.filter(
                filial__filial_pay__debtor_id=debror.id).aggregate(Sum('sotish_dollar'))['sotish_dollar__sum']
            # mijoz olgan tavarlar total kelish summasi
            total_olgan_tavar_kelish_sum = productfilials.filter(
                filial__filial_pay__debtor_id=debror.id).aggregate(Sum('som'))['som__sum']
            total_olgan_tavar_kelish_dollar = productfilials.filter(
                filial__filial_pay__debtor_id=debror.id).aggregate(Sum('dollar'))['dollar__sum']
            # tulanganlari
            total_tulagan_som = debtor_pay_history.filter(
                debtor_id=debror.id).aggregate(Sum('som'))['som__sum']
            total_tulagan_dollar = debtor_pay_history.filter(
                debtor_id=debror.id).aggregate(Sum('dollar'))['dollar__sum']

            if qarz_sum is None or qarz_dollar is None or total_tulagan_som is None or total_olgan_tavar_sum is None or total_olgan_tavar_dollar is None or total_tulagan_dollar is None or total_olgan_tavar_kelish_sum is None or total_olgan_tavar_kelish_dollar is None:
                qoldiq_qarz_sum = 0
                qoldiq_qarz_dollar = 0
                mijozdan_daromad_sum = 0
                mijozdan_daromad_dollar = 0

                all_clint_qarz_som += qarz_sum
                all_clint_qarz_dollar += qarz_dollar
                all_clint_tulagan_som += 0
                all_clint_tulagan_dollar += 0

            else:
                # qarz
                qoldiq_qarz_sum = float(qarz_sum) - float(total_tulagan_som)
                qoldiq_qarz_dollar = float(
                    qarz_dollar) - float(total_tulagan_dollar)
                # foyda
                mijozdan_daromad_sum = float(
                    total_olgan_tavar_sum) - float(total_olgan_tavar_kelish_sum)
                mijozdan_daromad_dollar = float(
                    total_olgan_tavar_dollar) - float(total_olgan_tavar_kelish_dollar)
                # sum
                all_clint_tulagan_som += float(total_tulagan_som)
                all_clint_tulagan_dollar += float(total_tulagan_dollar)
            # qarz sum
            all_clint_qarz_qoldiq_som += float(qoldiq_qarz_sum)
            all_clint_qarz_qoldiq_dollar += float(qoldiq_qarz_dollar)
            all_clint_daromad_som += float(mijozdan_daromad_sum)
            all_clint_daromad_dollar += float(mijozdan_daromad_dollar)

            dt = {
                'fio': debror.fio,
                'total_tulagan_som': total_tulagan_som,
                'total_tulagan_dollar': total_tulagan_dollar,
                'qarz_sum': qarz_sum,
                'qarz_dollar': qarz_dollar,
                'total_olgan_tavar_sum': total_olgan_tavar_sum,
                'total_olgan_tavar_dollar': total_olgan_tavar_dollar,
                'qoldiq_qarz_sum': qoldiq_qarz_sum,
                'qoldiq_qarz_dollar': qoldiq_qarz_dollar,
                'mijozdan_daromad_sum': mijozdan_daromad_sum,
                'mijozdan_daromad_dollar': mijozdan_daromad_dollar,
            }
            ll.append(dt)
        context = {
            'malumotlar': ll,
            'all_clint_qarz_som': all_clint_qarz_som,
            'all_clint_qarz_dollar': all_clint_qarz_dollar,
            'all_clint_tulagan_som': all_clint_tulagan_som,
            'all_clint_tulagan_dollar': all_clint_tulagan_dollar,
            'all_clint_qarz_qoldiq_som': all_clint_qarz_qoldiq_som,
            'all_clint_qarz_qoldiq_dollar': all_clint_qarz_qoldiq_dollar,
            'all_clint_daromad_som': all_clint_daromad_som,
            'all_clint_daromad_dollar': all_clint_daromad_dollar,
        }
        return render(request, 'get_ltv_data.html', context)

    except Exception as e:
        print(e)
        return JsonResponse({'error': 'error'})


class Products(LoginRequiredMixin, TemplateView):
    template_name = 'product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        get_data = self.request.GET.get
        # page_number = get_data('page')

        if get_data("filial-name") == "Barcha filiallar":
            products = ProductFilial.objects.all().order_by('id')
            context['current_filial'] = "Barcha filiallar"
        elif get_data("filial-name") is None:
            products = ProductFilial.objects.filter(filial=1)
            context['current_filial'] = Filial.objects.get(pk=1).name
        else:
            products = ProductFilial.objects.filter(
                filial__name=get_data("filial-name")).order_by('id')
            context['current_filial'] = get_data("filial-name")

        if get_data("current_filial"):
            products = products.filter(filial__name=get_data("current_filial"))

        context['filials'] = Filial.objects.all()
        context['product'] = 'active'
        context['product_t'] = 'true'
        # context['page_obj'] = Paginator(products, 10).get_page(page_number)
        context['page_obj'] = products
        return context


def preparersearchview(request):
    preparer = request.POST.get('preparersearch')
    context = {

    }
    products = ProductFilial.objects.filter(ombor=True, preparer=preparer).select_related('group')
    context['ombor'] = 'active'
    context['ombor_t'] = 'true'
    context['ombors'] = products
    context['total_som'] = products.aggregate(Sum('som'))['som__sum']
    context['total_dollar'] = products.aggregate(Sum('dollar'))['dollar__sum']
    context['total_som_sotish'] = products.aggregate(foo=Coalesce(Sum('sotish_som'), 0.00))['foo']
    context['total_dollar_sotish'] = products.aggregate(foo=Coalesce(Sum('sotish_dollar'), 0.00))['foo']
    context['total_quantity'] = products.aggregate(Sum('quantity'))['quantity__sum']
    return render(request, 'ombor.html', context)


def filterview(request):
    start_date = request.POST.get('from')
    end_date = request.POST.get('to')
    get_data = request.GET.get

    # page_number = get_data('page')
    context = {

    }
    if get_data("filial-name") == "Barcha filiallar":
        products = ProductFilial.objects.filter(expired_date__range=[start_date, end_date]).order_by('id')
        context['current_filial'] = "Barcha filiallar"
    elif get_data("filial-name") is None:
        products = ProductFilial.objects.filter(filial=1, expired_date__range=[start_date, end_date])
        context['current_filial'] = Filial.objects.get(pk=1).name
    else:
        products = ProductFilial.objects.filter(
            filial__name=get_data("filial-name"), expired_date__range=[start_date, end_date]).order_by('id')
        context['current_filial'] = get_data("filial-name")

    if get_data("current_filial"):
        print(000000)
        if start_date and end_date:
            print(1231)
            print(start_date)
            products = products.filter(
                Q(filial__name=get_data("current_filial")) | Q(expired_date__range=[start_date, end_date]))
        else:
            products = None

    context['filials'] = Filial.objects.all()
    context['product'] = 'active'
    context['product_t'] = 'true'
    # context['page_obj'] = Paginator(products, 10).get_page(page_number)
    context['page_obj'] = products
    return render(request, 'product.html', context)


class ProductShopView(LoginRequiredMixin, TemplateView):
    template_name = 'product-shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filial_name = self.request.GET.get('filial-name')
        # page_number = self.request.GET.get('page')
        date1 = self.request.GET.get('date1')
        date2 = self.request.GET.get('date2')

        products = ProductFilial.objects.annotate(shop_quantity=Coalesce(
            Sum('cart__quantity'),
            0
        )).filter(shop_quantity__gt=0).select_related('group', 'filial').order_by('id')

        if filial_name is None:
            products = products.filter(filial=2)
            context['current_filial'] = Filial.objects.get(id=1).name

        if filial_name and filial_name != 'Barcha filiallar':
            products = products.filter(filial__name=filial_name)
            context['current_filial'] = filial_name

        if date1 and date2:
            products = products.annotate(shop_quantity=Coalesce(
                Sum('cart__quantity', filter=Q(cart__date__range=(date1, date2))),
                0
            )).filter(shop_quantity__gt=0).select_related('group', 'filial').order_by('id')

            context['date1'] = date1
            context['date2'] = date2

        # context['page_obj'] = Paginator(products, 10).get_page(page_number)
        context['page_obj'] = products
        context['filials'] = Filial.objects.all()
        context['product'] = 'active'
        context['product_t'] = 'true'
        return context


class Filials(LoginRequiredMixin, TemplateView):
    template_name = 'filial.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        som = 0
        dollar = 0

        filials = Filial.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte),
                'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte)
            }
        )

        for f in filials:
            if f.naqd_dollar:
                dollar += f.naqd_dollar
            if f.nasiya_dollar:
                dollar += f.nasiya_dollar
            if f.plastik:
                dollar += f.plastik
            if f.transfer:
                dollar += f.transfer
            if f.skidka_dollar:
                dollar -= f.skidka_dollar
            print("skidka_dollar", f.skidka_dollar)
            print("pay_dollar", f.pay_dollar)

        context = super().get_context_data(**kwargs)
        context['filial'] = 'active'
        context['filial_t'] = 'true'
        context['som'] = som
        context['dollar'] = dollar
        context['filials'] = filials
        context['successform'] = False

        return context


class WareFakturas(LoginRequiredMixin, TemplateView):
    template_name = 'warefaktura.html'

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warefakturas'] = 'active'
        context['warefakturas_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(status=1)
        context['fakturaitems'] = FakturaItem.objects.all()

        return context


class WareFakturaTarix(LoginRequiredMixin, TemplateView):
    template_name = 'warefakturatarix.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['warefakturatarix'] = 'active'
        context['warefakturatarix_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(
            date__gte=gte, date__lte=lte)

        return context


class Saler(LoginRequiredMixin, TemplateView):
    template_name = 'saler.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        salers = UserProfile.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
            }
        )
        som = 0
        dollar = 0
        for f in salers:
            if f.naqd_som:
                som += f.naqd_som
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
            else:
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
            if f.naqd_dollar:
                dollar += f.naqd_dollar
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
            else:
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
        context = super().get_context_data(**kwargs)
        context['saler'] = 'active'
        context['saler_t'] = 'true'
        context['salers'] = salers
        context['som'] = som
        context['dollar'] = dollar
        return context


class Ombor(LoginRequiredMixin, TemplateView):
    template_name = 'ombor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = ProductFilial.objects.filter(ombor=True).select_related('group')
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['ombors'] = products
        context['total_som'] = products.aggregate(Sum('som'))['som__sum']
        context['total_som_sotish'] = products.aggregate(foo=Coalesce(Sum('sotish_som'), 0.00))['foo']
        context['total_dollar_sotish'] = products.aggregate(foo=Coalesce(Sum('sotish_dollar'), 0.00))['foo']
        context['total_dollar'] = products.aggregate(Sum('dollar'))[
            'dollar__sum']
        context['total_quantity'] = products.aggregate(Sum('quantity'))[
            'quantity__sum']
        return context


class OmborQabul(LoginRequiredMixin, TemplateView):
    template_name = 'omborqabul.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['wares'] = Receive.objects.filter(date__gte=gte, date__lte=lte)
        for i in context['wares']:
            print(i.get_total_selling_price)
        return context


# class FakturaListView(LoginRequiredMixin, TemplateView):
#     template_name = 'faktura.html'


class OmborMinus(LoginRequiredMixin, TemplateView):
    template_name = 'omborminus.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['ombors'] = ProductFilial.objects.filter(quantity__lte=100)
        context['total_som'] = ProductFilial.objects.filter(
            quantity__lte=100).aggregate(Sum('som'))['som__sum']
        context['total_dollar'] = ProductFilial.objects.filter(
            quantity__lte=100).aggregate(Sum('dollar'))['dollar__sum']
        context['total_soni'] = ProductFilial.objects.aggregate(Sum('quantity'))[
            'quantity__sum']

        return context


class FakturaListView(LoginRequiredMixin, TemplateView):
    template_name = 'faktura.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['invoices'] = Faktura.objects.filter(status__in=(1, 2, 3))
        context['items'] = FakturaItem.objects.all().order_by('-id')
        return context


class Recieves(LoginRequiredMixin, TemplateView):
    template_name = 'recieves.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['recieves'] = Receive.objects.all().order_by('-id')
        context['recieveitems'] = ReceiveItem.objects.all().order_by('-id')[:1000]

        return context


class FakturaTarix(LoginRequiredMixin, TemplateView):
    template_name = 'fakturatarix.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(
            date__gte=gte, date__lte=lte)

        return context


def DataFak(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    wares = Faktura.objects.filter(date__gte=date1, date__lte=date2)
    wr = []
    for w in wares:
        t = {
            'id': w.id,
            'summa': w.summa,
            'filial': w.filial.name,
            'difference': w.difference,
            'date': w.date.strftime("%d-%m-%y %I:%M")

        }
        wr.append(t)
    dt1 = {
        'wares': wr
    }
    return JsonResponse(dt1)


def GetFakturaItem(request):
    data = json.loads(request.body)
    id = data['id']
    items = FakturaItem.objects.filter(faktura_id=id)
    it = []
    for i in items:
        its = {
            'id': i.id,
            'product': i.product.name,
            'price': i.price,
            'quantity': i.quantity
        }
        it.append(its)
    dt1 = {
        'items': it
    }
    return JsonResponse(dt1)


class Table(TemplateView):
    template_name = 'table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = 'active'
        context['table_t'] = 'true'

        return context


class DataTable(TemplateView):
    template_name = 'datatable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datatable'] = 'active'
        context['datatable_t'] = 'true'

        return context


class Hodim(LoginRequiredMixin, TemplateView):
    template_name = 'hodim.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hodim'] = 'active'
        context['hodim_t'] = 'true'
        context['salers'] = UserProfile.objects.filter(~Q(staff=1))
        context['filials'] = Filial.objects.all()

        return context


class Debtors(LoginRequiredMixin, TemplateView):
    template_name = 'debtor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debtor'] = 'active'
        context['debtor_t'] = 'true'
        context['debtors'] = Debtor.objects.all()
        context['total_som'] = Debtor.objects.aggregate(Sum('som'))['som__sum']
        context['total_dollar'] = Debtor.objects.aggregate(Sum('dollar'))[
            'dollar__sum']

        return context


class Delivers(LoginRequiredMixin, TemplateView):
    template_name = 'deliver.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deliver'] = 'active'
        context['deliver_t'] = 'true'
        context['delivers'] = Deliver.objects.all()

        return context


class FakturaYoqlama(LoginRequiredMixin, TemplateView):
    template_name = 'fakturayoqlama.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kamomads'] = Kamomad.objects.all()
        context['faktura_yoqlama'] = 'active'
        context['faktura_yoqlama_t'] = 'true'
        return context


class Profile(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_t'] = 'true'
        # context['user'] = UserProfile.objects.get(username)

        return context


class ProfileSetting(TemplateView):
    template_name = 'profile-setting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_t'] = 'true'

        return context


class SweetAlert(TemplateView):
    template_name = 'sweet-alert.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sweet_alert'] = 'active'
        context['sweet_alert_t'] = 'true'

        return context


class Date(TemplateView):
    template_name = 'date.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = 'active'
        context['date_t'] = 'true'

        return context


class Widget(TemplateView):
    template_name = 'widget.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widget'] = 'active'
        context['widget_t'] = 'true'

        return context


@csrf_exempt
def Login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Login yoki Parol notogri kiritildi!')
            return redirect('login')
    else:
        return render(request, 'login.html')


def Logout(request):
    logout(request)
    messages.success(request, "Tizimdan chiqish muvaffaqiyatli yakunlandi!")
    return redirect('login')


def kassa(request):
    if request.method == 'POST':
        start_time = request.POST.get('date1')
        end_time = request.POST.get('date2')

        incomes = CashboxReceive.objects.filter(
            status='accepted', date__range=[start_time, end_time])
        payments = Chiqim.objects.filter(qachon__range=[start_time, end_time])
        total_income = incomes.aggregate(
            foo=Coalesce(Sum('total_sum'), 0))['foo']
        total_payment = payments.aggregate(
            foo=Coalesce(Sum('qancha_dol'), 0))['foo']
        balance = total_income - total_payment

        data = {
            "total_income": total_income,
            "total_payment": total_payment,
            "balance": balance
        }
        return JsonResponse(data)

    month = datetime.now().month

    incomes = CashboxReceive.objects.filter(
        status='accepted', date__month=month)
    payments = Chiqim.objects.filter(qachon__month=month)
    total_income = incomes.aggregate(foo=Coalesce(Sum('total_sum'), 0))['foo']
    total_payment = payments.aggregate(
        foo=Coalesce(Sum('qancha_dol'), 0, output_field=FloatField()))['foo']
    balance = total_income - total_payment
    chiqim_turlari = ChiqimTuri.objects.all()

    context = {
        'incomes': incomes,
        'payments': payments,
        'total_income': total_income,
        'total_payment': total_payment,
        'balance': balance,
        'chiqim_turlari': chiqim_turlari,
        'kassa': 'active',
        'kassa_t': 'true'
    }

    return render(request, 'kassa.html', context)


def kassa_filter_incomes(request):
    if request.method == 'POST':
        start_time = request.POST.get('date1')
        end_time = request.POST.get('date2')
        incomes = CashboxReceive.objects.filter(
            status='accepted', date__range=[start_time, end_time])
        return render(request, 'kassa_filters/incomes.html', {"incomes": incomes})


def kassa_filter_payments(request):
    if request.method == 'POST':
        start_time = request.POST.get('date1')
        end_time = request.POST.get('date2')
        payments = Chiqim.objects.filter(qachon__range=[start_time, end_time])
        return render(request, 'kassa_filters/payments.html', {"payments": payments})


def hodimga_qarz(request):
    if request.method == "POST":
        kassa_var = Kassa.objects.first()
        uslub = request.POST['uslub']

        if uslub == 'yangi':

            hodim_id = request.POST['hodim_id']
            qancha_som = request.POST.get('qancha_som')
            qancha_dol = request.POST.get('qancha_dol')
            izox = request.POST.get('izox')

            if qancha_som.isdigit() or qancha_dol.isdigit():

                if not qancha_dol.isdigit():
                    qancha_dol = 0

                if not qancha_som.isdigit():
                    qancha_som = 0

                if int(qancha_som) > 0 or int(qancha_dol) > 0:
                    qarz = HodimQarz.objects.create(
                        hodim_id=hodim_id, izox=izox)

                    if qancha_som:
                        qarz.qancha_som += int(qancha_som)
                        kassa_var.som -= int(qancha_som)

                    if qancha_dol:
                        qarz.qancha_dol += int(qancha_dol)
                        kassa_var.dollar -= int(qancha_dol)

                    qarz.save()
                    kassa_var.save()

                    messages.info(request, "Qarz berildi!")
                    messages.info(
                        request, f"hodim: {HodimModel.objects.get(id=hodim_id).toliq_ism_ol()}.")
                    messages.info(request, f"So'm: {qancha_som}")
                    messages.info(request, f"$: {qancha_dol}")

                else:
                    messages.info(request, "0 miqdorda qarz bermoqchimisiz! 🤔")

            else:
                messages.info(
                    request, "😡 Biror pul miqdorini kiritib keyi bosing!")

        else:

            qarz_id = request.POST['qarz_id']
            hodim_id = request.POST['hodim_id']
            qancha_som = request.POST.get('qancha_som')
            qancha_dol = request.POST.get('qancha_dol')
            izox = request.POST['izox']

            qarz = HodimQarz.objects.get(id=qarz_id)

            if qancha_som:
                qarz.qaytargani_som += int(qancha_som)
                kassa_var.som += int(qancha_som)

            if qancha_dol:
                qarz.qaytargani_dol += int(qancha_dol)
                kassa_var.dollar += int(qancha_dol)

            qarz.qaytargandagi_izox = izox
            qarz.save()
            kassa_var.save()
            qarz.qarzni_tekshir()

            messages.info(request, "To'lov qabul qilindi")

            return redirect(f'/hodim-qarzlari/?hodim_id={hodim_id}')

        return redirect('/kassa/')


def hodim_qarzlari(request):
    hodim_id = request.GET['hodim_id']
    hodim = HodimModel.objects.get(id=hodim_id)
    qarzlari = hodim.hodimqarz_set.filter(tolandi=False)

    return render(request, 'hodim_qarzlari.html', {'hodim': hodim, 'qarzlari': qarzlari})


def chiqim_qilish(request):
    """ Kassadan chiqim qiladi """

    if request.method == 'POST':
        chiqim_turi = request.POST['chiqim_turi']
        qayerga = request.POST.get('to_where')
        qancha_dol = request.POST.get('qancha_dol')
        izox = request.POST['izox']

        chiqim = Chiqim.objects.create(category_id=chiqim_turi,
                                       to_where=qayerga,
                                       qancha_dol=qancha_dol,
                                       izox=izox)

        return redirect('/kassa/')


def oylik_tolash(request):
    if request.method == "POST":
        hodim_id = request.POST['hodim_id']
        kassa_var = Kassa.objects.first()
        hodim = HodimModel.objects.get(id=hodim_id)

        OylikTolov.objects.create(hodim_id=hodim_id, pul=hodim.oylik)

        kassa_var.som -= hodim.oylik
        kassa_var.save()

        return redirect('/kassa/')


# 998997707572 len = 12
def checkPhone(phone):
    try:
        int(phone)
        return (True, phone) if len(phone) >= 12 else (False, None)
    except:
        return False, None


# for fio and qarz som


def sms_text_replace(sms_text, customer):
    try:
        dollar = '{:,}'.format(round(float(customer.dollar), 2))
        phones = "\t+".join(UserProfile.objects.filter(filial=customer.last_filial).values_list('phone', flat=True))
        sms_texts = str(sms_text).format(name=customer.fio, dollar=dollar, phones=phones)
    except Exception as e:
        print(e)

    return sms_texts


# for fio


def sms_text_replaces(sms_text, customer):
    try:
        phones = "\t+".join(UserProfile.objects.filter(filial=customer.last_filial).values_list('phone', flat=True))
        sms_texts = str(sms_text).format(
            name=customer.fio, dollar=round(customer.dollar, 2), phones=phones)
    except Exception as e:
        print(e)

    return sms_texts


# sms sender  if date today


def schedular_sms_send():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.DEADLINE_SMS
        vaqt = datetime.now().date()
        debtors = Debtor.objects.filter(
            debt_return__day=vaqt.day, debt_return__month=vaqt.month)

        for debtor in debtors:
            sms_text = sms_text_replaces(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)


# old deptors
def schedular_sms_send_olds():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.OLD_DEADLINE_SMS
        vaqt = datetime.now().date()

        debtors = Debtor.objects.filter(
            debt_return__day__lt=vaqt.day, debt_return__month__lte=vaqt.month)

        for debtor in debtors:
            sms_text = sms_text_replaces(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                result = sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)


# send 3days agos deptors


def schedular_sms_send_alert():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.THREE_DAY_AGO_SMS
        # 3kun oldingi kunlar
        thire_day_future = datetime.today() + timedelta(days=3)
        thire_day_future_date = thire_day_future.date()
        debtors = Debtor.objects.filter(
            debt_return__day=thire_day_future_date.day, debt_return__month=thire_day_future_date.month)

        for debtor in debtors:
            sms_text = sms_text_replace(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)


class SavdoTahlil(LoginRequiredMixin, TemplateView):
    template_name = 'savdo_tahlil.html'
    print(5%2)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['savdo_tahlil'] = 'active'
        context['savdo_tahlil_t'] = 'true'


        return context


def get_savdo_tahlil(request):
    month = datetime.now().month

    date_start = request.GET.get('start')
    date_end = request.GET.get('end')

    print(date_start, date_end)

    if date_start is not None and date_end is not None:
        shops = Shop.objects.filter(date__gte=date_start, date__lte=date_end)
        carts = Cart.objects.filter(date__gte=date_start, date__lte=date_end)
    else:
        shops = Shop.objects.filter(date__month=month)
        carts = Cart.objects.filter(date__month=month)
    branches = Filial.objects.all()
    productfilials = ProductFilial.objects.all()

    data_for_table = []
    for branch in branches:
        jami_qoldiq_tannarx_som = productfilials.filter(
            filial=branch).aggregate(foo=Sum(F("som") * F("quantity")))['foo']
        jami_qoldiq_tannarx_dollar = productfilials.filter(
            filial=branch).aggregate(foo=Sum(F("dollar") * F("quantity")))['foo']
        jami_qoldiq_sotish_som = productfilials.filter(filial=branch).aggregate(
            foo=Sum(F("sotish_som") * F("quantity")))['foo']
        jami_qoldiq_sotish_dollar = productfilials.filter(filial=branch).aggregate(
            foo=Sum(F("sotish_dollar") * F("quantity"),
                    ))['foo']
        jami_sotilgan_mahsulot_som = shops.filter(filial=branch).aggregate(foo=Sum(
            F("naqd_som") + F("nasiya_som") + F("transfer") + F("plastik") - F("skidka_som"),

        ))['foo']

        jami_sotilgan_mahsulot_dollar = shops.filter(filial=branch).aggregate(foo=Sum(
            F("naqd_dollar")  +
            F("nasiya_dollar") - F("skidka_dollar"), output_field=FloatField()
        ))['foo']

        if jami_sotilgan_mahsulot_dollar is None:
            jami_sotilgan_mahsulot_dollar = 0
        if jami_sotilgan_mahsulot_som is None:
            jami_sotilgan_mahsulot_som = 0

        sotilgan_tannarx_som = carts.filter(shop__filial=branch).aggregate(foo=Sum(
            F("arrival_price_som") * F("quantity"),
            output_field=FloatField()
        ))['foo']
        if sotilgan_tannarx_som is None:
            sotilgan_tannarx_som = 0

        jami_yalpi_daromad_som = jami_sotilgan_mahsulot_som - sotilgan_tannarx_som

        sotilgan_tannarx = carts.filter(shop__filial=branch).aggregate(foo=Sum(
            F("arrival_price") * F("quantity"),
            output_field=FloatField()
        ))['foo']
        if sotilgan_tannarx is None:
            sotilgan_tannarx = 0

        jami_yalpi_daromad_dollar = jami_sotilgan_mahsulot_dollar - sotilgan_tannarx

        jami_qarzdorlik_savdo_som = shops.filter(
            filial=branch).aggregate(foo=Sum("nasiya_som"))['foo']
        jami_qarzdorlik_savdo_dollar = shops.filter(
            filial=branch).aggregate(foo=Sum("nasiya_dollar"))['foo']

        if jami_qoldiq_tannarx_som is None:
            jami_qoldiq_tannarx_som = 0
        if jami_qoldiq_tannarx_dollar is None:
            jami_qoldiq_tannarx_dollar = 0
        if jami_qoldiq_sotish_som is None:
            jami_qoldiq_sotish_som = 0
        if jami_qoldiq_sotish_dollar is None:
            jami_qoldiq_sotish_dollar = 0
            jami_qoldiq_tannarx_dollar = 0
        if jami_sotilgan_mahsulot_som is None:
            jami_sotilgan_mahsulot_som = 0
        if jami_yalpi_daromad_som is None:
            jami_yalpi_daromad_som = 0
        if jami_yalpi_daromad_dollar is None:
            jami_yalpi_daromad_dollar = 0
        if jami_qarzdorlik_savdo_som is None:
            jami_qarzdorlik_savdo_som = 0
        if jami_qarzdorlik_savdo_dollar is None:
            jami_qarzdorlik_savdo_dollar = 0

        data_for_table.append(
            {
                "name": f"{branch.name}",
                "jami_qoldiq_tannarx_som": jami_qoldiq_tannarx_som,
                "jami_qoldiq_tannarx_dollar": jami_qoldiq_tannarx_dollar,
                "jami_qoldiq_sotish_som": jami_qoldiq_sotish_som,
                "jami_qoldiq_sotish_dollar": jami_qoldiq_sotish_dollar,
                "jami_sotilgan_mahsulot_som": jami_sotilgan_mahsulot_som,
                "jami_sotilgan_mahsulot_dollar": jami_sotilgan_mahsulot_dollar,
                "jami_yalpi_daromad_som": jami_yalpi_daromad_som,
                "jami_yalpi_daromad_dollar": jami_yalpi_daromad_dollar,
                "jami_qarzdorlik_savdo_som": jami_qarzdorlik_savdo_som,
                "jami_qarzdorlik_savdo_dollar": jami_qarzdorlik_savdo_dollar
            }
        )

    total_qoldiq_tannarx_som = sum(
        branch['jami_qoldiq_tannarx_som'] for branch in data_for_table)
    if total_qoldiq_tannarx_som is None:
        total_qoldiq_tannarx_som = 0

    total_qoldiq_tannarx_dollar = sum(
        branch['jami_qoldiq_tannarx_dollar'] for branch in data_for_table)
    if total_qoldiq_tannarx_dollar is None:
        total_qoldiq_tannarx_dollar = 0

    total_qoldiq_sotish_som = sum(
        branch['jami_qoldiq_sotish_som'] for branch in data_for_table)
    if total_qoldiq_sotish_som is None:
        total_qoldiq_sotish_som = 0

    total_qoldiq_sotish_dollar = sum(
        branch.get('jami_qoldiq_sotish_dollar', 0) for branch in data_for_table)
    if total_qoldiq_sotish_dollar is None:
        total_qoldiq_sotish_dollar = 0

    total_sotilgan_mahsulot_som = sum(
        branch['jami_sotilgan_mahsulot_som'] for branch in data_for_table)
    if total_sotilgan_mahsulot_som is None:
        total_sotilgan_mahsulot_som = 0

    total_sotilgan_mahsulot_dollar = sum(
        branch['jami_sotilgan_mahsulot_dollar'] for branch in data_for_table)
    if total_sotilgan_mahsulot_dollar is None:
        total_sotilgan_mahsulot_dollar = 0

    total_yalpi_daromad_som = sum(
        branch['jami_yalpi_daromad_som'] for branch in data_for_table)
    if total_yalpi_daromad_som is None:
        total_yalpi_daromad_som = 0

    total_yalpi_daromad_dollar = sum(
        branch['jami_yalpi_daromad_dollar'] for branch in data_for_table)
    if total_yalpi_daromad_dollar is None:
        total_yalpi_daromad_dollar = 0

    total_qarzdorlik_savdo_som = sum(
        branch['jami_qarzdorlik_savdo_som'] for branch in data_for_table)
    if total_qarzdorlik_savdo_som is None:
        total_qarzdorlik_savdo_som = 0

    total_qarzdorlik_savdo_dollar = sum(
        branch['jami_qarzdorlik_savdo_dollar'] for branch in data_for_table)
    if total_qarzdorlik_savdo_dollar is None:
        total_qarzdorlik_savdo_dollar = 0

    total_data = {
        "total_qoldiq_tannarx_som": total_qoldiq_tannarx_som,
        "total_qoldiq_tannarx_dollar": total_qoldiq_tannarx_dollar,
        "total_qoldiq_sotish_som": total_qoldiq_sotish_som,
        "total_qoldiq_sotish_dollar": total_qoldiq_sotish_dollar,
        "total_sotilgan_mahsulot_som": total_sotilgan_mahsulot_som,
        "total_sotilgan_mahsulot_dollar": total_sotilgan_mahsulot_dollar,
        "total_yalpi_daromad_som": total_yalpi_daromad_som,
        "total_yalpi_daromad_dollar": total_yalpi_daromad_dollar,
        "total_qarzdorlik_savdo_som": total_qarzdorlik_savdo_som,
        "total_qarzdorlik_savdo_dollar": total_qarzdorlik_savdo_dollar
    }

    context = {
        "data": data_for_table,
        "total_data": total_data
    }

    return render(request, 'get_savdo_tahlil.html', context)


def chart_savdo_tahlil(request):
    today = date.today()
    shops = Shop.objects.filter(date__year=today.year)
    carts = Cart.objects.filter(date__year=today.year)
    get_sum = Sum(F("naqd_dollar") + F("transfer") + F("plastik") +F("naqd_som") +F("nasiya_som") +
            F("nasiya_dollar") - F("skidka_dollar")- F("skidka_som"), output_field=IntegerField())

    total_income = [shops.filter(
        date__month=i + 1).aggregate(foo=get_sum)['foo'] for i in range(12)]
    total_income = [0 if item is None else item for item in total_income]

    get_arrival_sum = Sum(F("arrival_price") * F("quantity")+F("arrival_price_som") * F("quantity"),
                          output_field=IntegerField())
    arrival_sum = [carts.filter(
        date__month=i + 1).aggregate(foo=get_arrival_sum)['foo'] for i in range(12)]
    arrival_sum = [0 if item is None else item for item in arrival_sum]

    yalpi_daromad = [total_income[i] - arrival_sum[i] for i in range(12)]

    data = {
        'total_income': total_income,
        'yalpi_daromad': yalpi_daromad
    }
    print(data)

    return JsonResponse(data)


def income_status_change(request):
    income_id = int(request.GET.get('id'))
    income = CashboxReceive.objects.get(id=income_id)
    income.status = request.GET.get('status')
    income.save()
    filial = int(request.GET.get('filial'))
    return redirect(f'/filialinfo/{filial}/')


@transaction.atomic
def get_data_from_xlsx(request):
    if request.method == 'POST':
        form = AddFilialForm(request.POST, request.FILES)
        if form.is_valid():
            my_list = []
            try:
                input_excel = request.FILES['excel_file']
                workbook = xlrd.open_workbook(file_contents=input_excel.read())
                sheet_name = workbook.sheet_names()[0]
                sheet = workbook.sheet_by_name(sheet_name)
                with transaction.atomic():
                    for rx in range(sheet.nrows):
                        row = [r.value for r in sheet.row(rx)]
                        row.pop(0)
                        my_list.append(row)

                my_list.pop(0)
                my_list.pop(0)
                filial_name = request.POST.get('filial')
                address = request.POST.get('address')
                if Filial.objects.filter(name=filial_name).exists():
                    raise Exception('Bu nomli filial allaqachon mavjud!')
                filial = Filial.objects.create(
                    name=filial_name, address=address)
                group_count = 0

                with transaction.atomic():
                    for i in my_list:

                        group, created = Groups.objects.get_or_create(
                            name=i[5])
                        if created is True:
                            group_count += 1

                        quantity = i[1] if isinstance(
                            i[1], float) or isinstance(i[1], int) else 0
                        # expired_date = i[-1] if isinstance(
                        #     i[-1], float) or isinstance(i[-1], int) else 0
                        selling_price = i[4] if isinstance(
                            i[4], float) or isinstance(i[4], int) else 0
                        selling_price_som = i[-3] if isinstance(
                            i[-3], float) or isinstance(i[-3], int) else 0
                        arrival_price = i[6] if isinstance(
                            i[6], float) or isinstance(i[6], int) else 0
                        arrival_price_som = i[-2] if isinstance(
                            i[6], float) or isinstance(i[6], int) else 0
                        if i[9]:
                            day, month, year = i[9].split('A')
                            expired_date = '-'.join([year, month, day])
                        else:
                            expired_date = None

                        if ProductFilial.objects.filter(barcode=str(i[2])):
                            pass
                        else:

                            ProductFilial.objects.create(
                                name=i[0],
                                preparer=i[3],
                                sotish_som=selling_price_som,
                                som=arrival_price_som,
                                dollar=arrival_price,
                                sotish_dollar=selling_price,
                                barcode=str(i[2]),
                                filial=filial,
                                quantity=quantity,
                                min_count=10,
                                group=group,
                                expired_date=expired_date

                            )
                        print(i[0])

                        # Ombor uchun product
                        have_product = ProductFilial.objects.filter(ombor=True, barcode=i[2]).exists()
                        if not have_product:
                            ProductFilial.objects.create(
                                name=i[0],
                                preparer=i[3],
                                dollar=arrival_price,
                                sotish_dollar=selling_price,
                                sotish_som=selling_price_som,
                                som=arrival_price_som,
                                barcode=str(i[2]),
                                group=group,
                                ombor=True,
                                expired_date=expired_date
                            )

                return redirect('filial')

            except Exception as e:
                form.add_error(
                    None,
                    f"Xatolik mavjud: {e} Ma'lumotlar to'g'riligiga ishonch xosil qiling va sayt dasturchilariga bog'laning!")
                return render(request, 'filial.html', {'form': form})

        else:
            return render(request, 'filial.html', {'form': form})


def filial_chiqim_view(request):
    expenses = FilialExpense.objects.all()
    branches = Filial.objects.all()

    date1 = request.GET.get('date1')
    date2 = request.GET.get('date2')
    filial_name = request.GET.get('filial-name')
    current_filial = 'Barcha filiallar'

    if date1 and date2:
        expenses = expenses.filter(created_at__range=(date1, date2))

    if filial_name:
        current_filial = filial_name
        if filial_name != 'Barcha filiallar':
            expenses = expenses.filter(filial__name=filial_name)

    total_expenses = expenses.aggregate(foo=Coalesce(
        Sum('total_sum'),
        0
    ))['foo']

    context = {
        'filial': "active",
        'filial_t': "true",
        'filials': branches,
        'current_filial': current_filial,
        'total_expenses': total_expenses,
        'expenses': expenses,
    }

    return render(request, 'filial_chiqim.html', context)
