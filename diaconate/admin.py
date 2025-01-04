from django.contrib import admin

from .models import (
    Asset, AssetCategory, 
    AssetAttribute, AssetAttributeValue,
    TreasuryRequest, Audit,
    Transaction, Report,
)

# Register your models here.

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'source_of_item', 'location', 'condition')
    list_filter = ('category', 'location', 'condition', 'source_of_item', 'status')
    date_hierarchy = 'purchase_date'
    search_fields = ('name', 'value', 'description')


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
     

@admin.register(AssetAttribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category', )
    search_fields = ('name', )
    
    
@admin.register(AssetAttributeValue)
class AssetAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('asset', 'attribute', 'value')
    search_fields = ('asset__name', 'attribute__name', 'value')
    list_filter = ('attribute__category', )




@admin.register(TreasuryRequest)
class TreasuryRequestAdmin(admin.ModelAdmin):
    list_display = ('requested_by', 'asset', 'status', 'request_date', 'approved_by')
    list_filter = ('status', 'asset', 'approved_by')
    date_hierarchy = 'request_date'
    