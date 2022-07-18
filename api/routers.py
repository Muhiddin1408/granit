from rest_framework.routers import DefaultRouter
from .viewsets import *
from django.urls import path

router = DefaultRouter()
router.register('token', TokenViewset)
router.register('userprofile', UserProfileViewset)
router.register('filial', FilialViewset)
router.register('groups', GroupsViewset)
router.register('deliver', DeliverViewset)
router.register('products', Product_FilialViewset)
router.register('productfilial', ProductFilialViewset)
router.register('productstorage', ProductStorageViewSet)
router.register('receive', ReceiveViewset)
router.register('receiveitem', ReceiveItemViewset)
router.register('faktura', FakturaViewset)
router.register('fakturaitem', FakturaItemViewset)
router.register('shop', ShopViewset)
router.register('cart', CartViewset)
router.register('debtor', DebtorViewset)
# router.register('debthistory', DebtHistoryViewset)
router.register('debt', DebtViewset)
router.register('payhistory', PayHistoryViewset)
router.register('cartdebt', CartDebtViewset)
router.register('returnproduct', ReturnProductViewset)
router.register('changeprice', ChangePriceViewset)
router.register('changepriceitem', ChangePriceItemViewset)
router.register('returnproducttodeliver', ReturnProductToDeliverViewset)
router.register('returnproducttodeliveritem', ReturnProductToDeliverItemViewset)
router.register('cashbox-receive', CashboxReceiveViewSet)
router.register('filial-expense', FilialExpenseViewSet)
router.register('filial-expense-category', FilialExpenseCategoryViewSet)
router.register('hisobdan_chiqarish-filial', HisobdanChiqarishFilial)
router.register('hisobdan_chiqarish-ombor', HisobdanChiqarishOmborViewset)
router.register('qaytgan-product-ombor', QaytganProductOmborView)
router.register('yuq-faktura-submit', YuqFakturaSubmitViewset)
router.register('item_yuq-faktura', ItemViewset)

urlpatterns = [
	path('create-product-filial/<int:pk>/', CreateProductFilial.as_view(), name="create-product-filial"),
	# path('login', login)
]