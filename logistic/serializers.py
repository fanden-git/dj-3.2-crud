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
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')
        # создаем склад по его параметрам
        stock = Stock.objects.create(**validated_data)
        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        for position in positions:
            StockProduct.objects.create(stock=stock, **position)
        return stock


    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')
        # обновляем склад по его параметрам
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        existing_ids = [p.id for p in instance.positions.all()]
        for position_data in positions:
            position_id = position_data.get('id', None)
            if position_id in existing_ids:
                # обновляем существующую позицию
                position = StockProduct.objects.get(id=position_id)
                position.product = position_data.get('product', position.product)
                position.quantity = position_data.get('quantity', position.quantity)
                position.price = position_data.get('price', position.price)
                position.save()
            else:
                # создаем новую позицию
                StockProduct.objects.create(stock=instance, **position_data)
        return instance
