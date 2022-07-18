from django.forms import IntegerField
from rest_framework import serializers
from .models import *
from rest_framework.authtoken.models import Token
from django.db.models import Sum, F
from django.db.models.functions import Coalesce


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class MOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MOrder
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'staff', 'filial']


class FilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = '__all__'


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = '__all__'


class DeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliver
        fields = '__all__'


class ProductFilialSerializer(serializers.ModelSerializer):
    group = serializers.ReadOnlyField(source='group.name')
    class Meta:
        model = ProductFilial
        print()
        fields = (
            'id',
            'name',
            'preparer',
            'som',
            'sotish_som',
            'dollar',
            'sotish_dollar',
            'kurs',
            'barcode',
            'group',
            'filial',
            'measurement',
            'min_count',
            'quantity',
            'image',
            'expired_date',
        )


class TestProductFilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFilial
        fields = (
            'barcode',
            'quantity',
        )

class ProductFilialSerializerWithCourse(serializers.ModelSerializer):

    class Meta:
        model = ProductFilial
        fields = '__all__'


class ProductFilialBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFilial
        fields = (
            'id',
            'name',
            'barcode',
            'preparer',
            'group',
            'measurement'
        )
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['group'] = instance.group.name
        return data


class ReceiveSerializer(serializers.ModelSerializer):
    total_arrival_price_dollar = serializers.ReadOnlyField(source='get_total_arrival_price')
    total_arrival_price_som = serializers.ReadOnlyField(source='get_total_arrival_price_som')
    total_selling_price_dollar_sotish = serializers.ReadOnlyField(source='get_total_selling_price')
    total_selling_price_som_sotish = serializers.ReadOnlyField(source='get_total_selling_price_som')

    class Meta:
        model = Receive
        fields = (
            'id',
            'name',
            'deliver',
            'date',
            'status',
            'total_arrival_price_dollar',
            'total_arrival_price_som',
            'total_selling_price_dollar_sotish',
            'total_selling_price_som_sotish'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['deliver'] = instance.deliver.name
        return data


class ReceiveItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(max_length=125)
    name = serializers.CharField(max_length=125)
    # faktura = serializers.CharField(max_length=125)

    class Meta:
        model = ReceiveItem
        fields = (
            'id',
            'receive',
            'product',
            # 'faktura',
            'name',
            'dollar',
            'sotish_dollar',
            'quantity',
            'sotish_som',
            'som',
            'expired_date'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product'] = ProductFilialBaseSerializer(instance=instance.product).data
        return data

    def validate(self, attrs):
        print('kirdi')
        product = attrs.get("product")
        print(product)
        if not product:
            raise serializers.ValidationError("Product barcodi berilishi shart!")
        
        return attrs


class ProductStorageSerializer(serializers.ModelSerializer):
    quantity = serializers.ReadOnlyField(source='get_quantity')

    class Meta:
        model = ProductFilial
        fields = (
            'id',
            'name',
            'preparer',
            'group',
            'barcode',
            'quantity',
            'ombor',
            'dollar',
            'sotish_dollar',
            'filial',
            'sotish_som',
            'som',
            'expired_date'
        )
        # extra_kwargs = {
        #     'ombor': {'write_only': True}
        # }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['dollar'] = instance.dollar
        data['sotish_dollar'] = instance.sotish_dollar
        data['group'] = instance.group.name
        return data

    def validate(self, attrs):
        barcode = attrs.get("barcode")
        product_exists = ProductFilial.objects.filter(ombor=True, barcode=barcode).exists()
        if product_exists:
            raise serializers.ValidationError("Bu mahsulot omborda mavjud!")
        return attrs


class FakturaSerializer(serializers.ModelSerializer):
    total_arrival_price = serializers.ReadOnlyField(source='get_total_arrival_price')
    total_arrival_price_som = serializers.ReadOnlyField(source='get_total_arrival_price_som')
    total_selling_price = serializers.ReadOnlyField(source='get_total_selling_price')
    total_selling_price_som = serializers.ReadOnlyField(source='get_total_selling_price_som')
    total_diff = serializers.ReadOnlyField(source='get_total_diff')

    class Meta:
        model = Faktura
        fields = (
            'id',
            'date',
            'filial',
            'status',
            'total_arrival_price',

            'total_selling_price',
            'total_arrival_price_som',
            'total_selling_price_som',
            'total_diff'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['filial'] = instance.filial.name
        return data


class FakturaItemSerializer(serializers.ModelSerializer):
    price_diff = serializers.ReadOnlyField()
    product = serializers.CharField(max_length=200)
    # name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = FakturaItem
        fields = (
            'id',
            'faktura',
            'product',
            # 'name',
            'body_dollar',
            'dollar',
            'quantity',
            'price_diff',
            'body_som',
            'som',
            'expired_date'
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product'] = ProductFilialBaseSerializer(instance=instance.product).data
        return data
 
    def validate(self, attrs):
        print('kirdi')
        product = attrs.get("product")
        print(product)
        product1 = ProductFilial.objects.filter(barcode=product).last()
        print(product1)
        storage_quantity = product1.get_quantity
        quantity = attrs.get("quantity")
        if storage_quantity <= quantity:
            raise serializers.ValidationError("Omborda bu mahsulot buncha mavjud emas!")    
        return attrs


class FakturaItemReadSerializer(serializers.ModelSerializer):
    product = ProductFilialSerializer(read_only=True)

    class Meta:
        model = FakturaItem
        fields = '__all__'


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class DebtorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debtor
        fields = '__all__'


# class DebtHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DebtHistory
#         fields = '__all__'


class DebtSerializer(serializers.ModelSerializer):
    debtor = DebtorSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = Debt
        fields = '__all__'


class PayHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayHistory
        fields = '__all__'


class CartDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartDebt
        fields = '__all__'


class ReturnProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProduct
        fields = '__all__'


class ChangePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePrice
        fields = '__all__'


class ChangePriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePriceItem
        fields = '__all__'


class ReturnProductToDeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliver
        fields = '__all__'


class ReturnProductToDeliverItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliverItem
        fields = '__all__'


class KamomadModalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kamomad
        fields = '__all__'


class MCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCart
        fields = "__all__"


class FilialRetrieveSerializer(serializers.ModelSerializer):
    qoldiq_sotish_som = serializers.SerializerMethodField()
    qoldiq_sotish_dollar = serializers.SerializerMethodField()
    jami_savdo_sotish = serializers.SerializerMethodField()

    class Meta:
        model = Filial
        fields = '__all__'
    
    def get_qoldiq_sotish_som(self, obj):
        return obj.filial_product.all().aggregate(qoldiq=Sum(
            F("sotish_som") * F("quantity")
        ))['qoldiq']

    def get_qoldiq_sotish_dollar(self, obj):
        return obj.filial_product.all().aggregate(qoldiq=Sum(
            F('sotish_dollar') * F('quantity')
        ))['qoldiq']

        # qoldiq_dollarda = obj.filial_product.all().aggregate(foo=Coalesce(Sum(sotish_dollar * quantity), 0.00))['foo']
        # print(qoldiq_dollarda)

    def get_jami_savdo_sotish(self, obj):
        return obj.shop_set.aggregate(foo=Sum(
            F("naqd_dollar")+F("transfer")+F("plastik")+F("nasiya_dollar")-F("skidka_dollar"),
        ))['foo']


class CashboxReceiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashboxReceive
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['filial'] = instance.filial.name
        return data


class FilialExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilialExpense
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['filial'] = instance.filial.name
        data['category'] = instance.category.title
        return data


class FilialExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FilialExpenseCategory
        fields = '__all__'


class HisobdanChiqarishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hisobdan_cgiqarish_filial
        fields = '__all__'


class HisobdanChiqarishOmborSerializer(serializers.ModelSerializer):
    class Meta:
        model = HisobdanChiqarishOmbor
        fields = '__all__'


class QaytganProductOmborrSerializer(serializers.ModelSerializer):
    class Meta:
        model = QaytganProductOmbor
        fields = '__all__'


class YuqFakturaSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = YuqFakturaSubmit
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(label='ID', required=False)

    class Meta:
        model = Item
        fields = ['id', 'barcode', 'quantity']


class YuqFakturaCreateSubmitSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=True)

    class Meta:
        model = YuqFakturaSubmit
        fields = [
            'filial',
            'item'
        ]

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        print('asd', validated_data)
        items = validated_data.pop('item')
        instance = YuqFakturaSubmit.objects.create(
            filial=validated_data['filial']
        )
        for item in items:
            print(item)
            if item.get('id') and Item.objects.filter(id=item['id']).exists():
                item = Item.objects.filter(id=item['id']).first()
            else:
                item = Item.objects.create(barcode=item['barcode'], quantity=item['quantity'])
            instance.item.add(item)

        return instance

