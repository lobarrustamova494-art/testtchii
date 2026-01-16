# Annotation Shift Fix - Tuzatish

## Muammo

Foydalanuvchi rasmda ko'rsatdiki, annotation to'rtburchaklari 1 pozitsiya O'NGGA siljigan:

- A javob uchun to'rtburchak B pozitsiyasida
- B javob uchun to'rtburchak C pozitsiyasida
- va hokazo

## Sabab

`coordinate_mapper.py` faylida `first_bubble_offset_mm = 8` qiymati ishlatilgan edi.
Bu qiymat PDF generatordagi `xPos + 8` formulasiga mos keladi.

Lekin amalda, bu 8mm offset annotation koordinatalarini 1 bubble o'ngga siljitib yuborgan.

## Yechim

`first_bubble_offset_mm` qiymatini 8 dan 0 ga o'zgartirdik.

### O'zgarish:

**Fayl:** `backend/utils/coordinate_mapper.py`
**Qator:** ~80

```python
# OLDIN:
self.first_bubble_offset_mm = 8

# KEYIN:
self.first_bubble_offset_mm = 0  # FIXED: Was 8, changed to 0 to fix annotation shift
```

## Natija

Endi barcha bubble koordinatalari 8mm (1 bubble) CHAPGA siljiydi:

- Bubble A: 33mm → 25mm
- Bubble B: 41mm → 33mm
- Bubble C: 49mm → 41mm
- va hokazo

Bu o'ng tomonga siljigan to'rtburchaklarni kompensatsiya qiladi va ularni to'g'ri pozitsiyaga joylashtiradi.

## Test qilish

1. Backend'ni qayta ishga tushiring:

   ```bash
   cd backend
   python main.py
   ```

2. Yangi rasm yuklang va tekshiring

3. Annotated image'da to'rtburchaklar to'g'ri bubble'lar ustida bo'lishi kerak:
   - Yashil to'rtburchak = to'g'ri javob
   - Ko'k to'rtburchak = student to'g'ri belgilagan
   - Qizil to'rtburchak = student xato belgilagan

## Agar muammo hal bo'lmasa

Agar to'rtburchaklar hali ham noto'g'ri pozitsiyada bo'lsa:

1. Rasmni va natijalarni ko'rsating
2. Qaysi tomonga siljigan (chap yoki o'ng)?
3. Necha pozitsiyaga siljigan (1, 2, yoki boshqa)?

Bu ma'lumotlar bilan muammoni aniqroq hal qilishimiz mumkin.

## Qo'shimcha Tekshirish

Agar bu fix ishlamasa, keyingi qadamlar:

1. PDF generator'dagi `+8` offset'ni tekshirish
2. QR code layout ma'lumotlarini tekshirish
3. Image transformation/scaling'ni tekshirish
4. Actual PDF bubble pozitsiyalarini o'lchash
