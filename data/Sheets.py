from classes.FieldType import FieldType
SHEETS = [
    {
        '_name': 'manufacturers',
        'sheet_name': 'Производители',
        'location': ['A', 'B'],
        'fields': [
            {
                '_name': 'ID_manufacturer',
                'field_name': 'ID производителя',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'manufacturer_name',
                'field_name': 'Название производителя',
                'type': FieldType.string,
                'required': True
            },
        ]
    },
    {
        '_name': 'models',
        'sheet_name': 'Модели',
        'location': ['A', 'B', 'C', 'H', 'J'],
        'fields': [
            {
                '_name': 'ID_model',
                'field_name': 'ID модели',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_manufacturer',
                'field_name': 'ID производителя',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'name',
                'field_name': 'Название',
                'type': FieldType.string,
                'required': True
            },
            {
                '_name': 'description',
                'field_name': 'Описание',
                'type': FieldType.string,
                'required': False
            },
            {
                '_name': 'url',
                'field_name': 'Ссылка на фото',
                'type': FieldType.url,
                'required': False
            },
        ]
    },
    {
        '_name': 'cartridges',
        'sheet_name': 'Картриджи',
        'location': ['A', 'B', 'C', 'D', 'J'],
        'fields': [
            {
                '_name': 'ID_cartridge',
                'field_name': 'ID картриджа',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_manufacturer',
                'field_name': 'ID производителя',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_model',
                'field_name': 'ID модели',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'name',
                'field_name': 'Название',
                'type': FieldType.string,
                'required': True
            },
            {
                '_name': 'url',
                'field_name': 'Ссылка на фото',
                'type': FieldType.url,
                'required': False
            }
        ]
    },
    {
        '_name': 'evaporators',
        'sheet_name': 'Испарители',
        'location': ['A', 'B', 'C', 'D', 'J'],
        'fields': [
            {
                '_name': 'ID_evaporator',
                'field_name': 'ID испарителя',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_manufacturer',
                'field_name': 'ID производителя',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_model',
                'field_name': 'ID модели',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'name',
                'field_name': 'Название',
                'type': FieldType.string,
                'required': True
            },
            {
                '_name': 'url',
                'field_name': 'Ссылка на фото',
                'type': FieldType.url,
                'required': False
            }
        ]
    },
    {
        '_name': 'tanks',
        'sheet_name': 'Баки',
        'location': ['A', 'B', 'C', 'D', 'J'],
        'fields': [
            {
                '_name': 'ID_tank',
                'field_name': 'ID бака',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_manufacturer',
                'field_name': 'ID производителя',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_model',
                'field_name': 'ID модели',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'name',
                'field_name': 'Название',
                'type': FieldType.string,
                'required': True
            },
            {
                '_name': 'url',
                'field_name': 'Ссылка на фото',
                'type': FieldType.url,
                'required': False
            }
        ]
    },
    {
        '_name': 'liquids_brands',
        'sheet_name': 'Бренды жидкостей',
        'location': ['A', 'B'],
        'fields': [
            {
                '_name': 'ID_brand',
                'field_name': 'ID бренда',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'brand_name',
                'field_name': 'Название',
                'type': FieldType.string,
                'required': True
            }
        ]
    },
    {
        '_name': 'liquids',
        'sheet_name': 'Жидкости',
        'location': ['A', 'B', 'C', 'H', 'J'],
        'fields': [
            {
                '_name': 'ID_liquid',
                'field_name': 'ID жидкости',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_brand',
                'field_name': 'ID бренда',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'name',
                'field_name': 'Название',
                'type': FieldType.string,
                'required': True
            },
            {
                '_name': 'strength',
                'field_name': 'Крепость',
                'type': FieldType.string,
                'required': False
            },
            {
                '_name': 'url',
                'field_name': 'Ссылка на фото',
                'type': FieldType.url,
                'required': False
            },
        ]
    },
    {
        '_name': 'other',
        'sheet_name': 'Прочее',
        'location': ['A', 'B', 'C','J'],
        'fields': [
            {
                '_name': 'ID_element',
                'field_name': 'ID элемента',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'ID_manufacturer',
                'field_name': 'ID производителя',
                'type': FieldType.digit,
                'required': True
            },
            {
                '_name': 'name',
                'field_name': 'Название',
                'type': FieldType.string,
                'required': True
            },
            {
                '_name': 'url',
                'field_name': 'Ссылка на фото',
                'type': FieldType.url,
                'required': False
            }
        ]
    }
]