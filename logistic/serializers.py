from rest_framework import serializers
from logistic.models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['address', 'positions']

    def create(self, validated_data):
        positions = validated_data.pop('positions')
        stock = Stock.objects.create(**validated_data)
        for position in positions:
            StockProduct.objects.create(stock=stock, **position)
        return stock

    def update(self, instance, validated_data):
        positions = validated_data.pop('positions')
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        for position in positions:
            position_id = position.get('id', None)
            defaults = {'product': position.get('product'),
                        'quantity': position.get('quantity'),
                        'price': position.get('price')}
            StockProduct.objects.update_or_create(stock=instance, id=position_id, defaults=defaults)
        return instance
