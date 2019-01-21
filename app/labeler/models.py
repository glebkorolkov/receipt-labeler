from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers


class ShoeBox(models.Model):
    """Class for receipt batches (shoe boxes)"""

    # Database fields
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name_plural = "ShoeBoxes"

    def __str__(self):
        """Method that overrides default __str__ method"""
        return f"ShoeBox id:{self.id}"

    def receipts_range(self):
        """
        Method that calculates lower and upper boundaries for ids of receipts
        in the shoe box.

        Parameters
        ----------
        None

        Returns
        -------
        tuple
            Tuple with min and max receipt id for the shoe box
        """

        rids = [r.id for r in self.receipts.all()]
        return min(rids), max(rids)

    def from_receipt_id(self):
        """Same as self.receipts_range(). Returns lower boundary for id range"""
        return self.receipts_range()[0]

    def to_receipt_id(self):
        """Same as self.receipts_range(). Returns upper boundary for id range"""
        return self.receipts_range()[1]

    def num_receipts(self):
        """Method that returns number of receipts in the shoe box"""
        return self.receipts.count()

    @staticmethod
    def batch_create(num_receipts, skip_assigned=True, skip_labeled=True):
        """
        Method that automatically creates shoe boxes and assigns receipts to them.
        Can only be called from django shell. Go to folder containing manage.py. Run:
        $ python manage.py shell
        >> ShoeBox.batch_create(100, True, False)

        Parameters
        ----------
        num_receipts : int
            Number of receipts in each shoe box
        skip_assigned : boolean
            Exclude previously assigned receipts if True
        skip_labeled : boolean
            Exclude previously labeled receipts if True

        Return
        ------
        tuple
            (number of generated shoe boxes, total receipts assigned)
        """

        # Retrieve all receipts
        receipts = Receipt.objects
        # Filter out assigned or labeled receipts or both
        if skip_assigned:
            receipts = receipts.filter(shoebox__isnull=True)
        if skip_labeled:
            receipts = receipts.exclude(labels=None)
        # Make chunks
        rids = [r.id for r in receipts.all()]
        chunks = make_chunks(rids, num_receipts)
        # Retrieve boxes
        boxes = ShoeBox.objects.all()
        # Delete existing boxes if reassigning boxes
        if not skip_assigned:
            boxes.delete()
        # Create boxes and assign receipts
        for chunk in chunks:
            box = ShoeBox()
            box.save()
            box_receipts = receipts.filter(id__in=chunk).all()
            box_receipts.update(shoebox=box)
        return len(list(chunks)), receipts.count()


class Receipt(models.Model):
    """Database receipt class"""

    # Database fields
    id = models.BigIntegerField(primary_key=True)
    receipt_code = models.CharField(unique=True, max_length=64)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    date_add = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    shoebox = models.ForeignKey(ShoeBox, null=True, on_delete=models.DO_NOTHING, related_name='receipts')

    label_names = ('merchant', 'amount', 'sub_total', 'tax', 'date')

    def clean_labels(self):
        """Method that deletes all labels associated with receipt"""
        if hasattr(self, 'labels'):
            self.labels.delete()
        for word in self.words.all():
            if hasattr(word, 'labels'):
                word.labels.delete()

    def label_missing(self, label):
        """Method that returns true if passed label was assigned as missing"""
        if not hasattr(self, 'labels'):
            return False
        return getattr(self.labels, label+'_missing')

    @property
    def label_missing_merchant(self):
        return self.label_missing('merchant')

    @property
    def label_missing_amount(self):
        return self.label_missing('amount')

    @property
    def label_missing_sub_total(self):
        return self.label_missing('sub_total')

    @property
    def label_missing_tax(self):
        return self.label_missing('tax')

    @property
    def label_missing_date(self):
        return self.label_missing('date')

    def label_broken(self, label):
        """Method that returns true if passed label was assigned as broken"""
        if not hasattr(self, 'labels'):
            return False
        return getattr(self.labels, label+'_broken')

    @property
    def label_broken_merchant(self):
        return self.label_broken('merchant')

    @property
    def label_broken_amount(self):
        return self.label_broken('amount')

    @property
    def label_broken_sub_total(self):
        return self.label_broken('sub_total')

    @property
    def label_broken_tax(self):
        return self.label_broken('tax')

    @property
    def label_broken_date(self):
        return self.label_broken('date')

    def label_val(self, label, sep=''):
        """
        Method that generates values from assigned labels taking account of their order

        Parameters
        ----------
        label : str
            Label name (e.g. amount)
        sep : str
            Separator for joining labels

        Return
        ------
        str
            Label value
        """

        words = self.words.filter(**{'labels__'+label: True})
        vals = [(word.text, getattr(word.labels, 'merchant_rank')) for word in words]
        vals.sort(key=lambda x: x[1])
        if label == 'merchant':
            sep = ' '
        return sep.join([val[0] for val in vals])

    @property
    def label_val_merchant(self):
        return self.label_val('merchant')

    @property
    def label_val_amount(self):
        return self.label_val('amount')

    @property
    def label_val_sub_total(self):
        return self.label_val('sub_total')

    @property
    def label_val_tax(self):
        return self.label_val('tax')

    @property
    def label_val_date(self):
        return self.label_val('date')

    def label_input(self, label):
        """
        Method that generates values of hidden inputs for template.

        Inputs
        ------
        label : str
            Label name

        Return
        ------
        str
            Label value consisting of concatenated word ids, e.g. 23|35
        """

        if self.label_missing(label):
            return "m"
        elif self.label_broken(label):
            return "b"
        words = self.words.filter(**{'labels__'+label: True})
        if len(words) == 0:
            return ""
        ids = [(word.id, getattr(word.labels, 'merchant_rank')) for word in words]
        ids.sort(key=lambda x: x[1])
        return "|".join([str(elem[0]) for elem in ids])

    @property
    def label_input_merchant(self):
        return self.label_input('merchant')

    @property
    def label_input_amount(self):
        return self.label_input('amount')

    @property
    def label_input_sub_total(self):
        return self.label_input('sub_total')

    @property
    def label_input_tax(self):
        return self.label_input('tax')

    @property
    def label_input_date(self):
        return self.label_input('date')

    @property
    def looks_ok(self):
        unlabeled_counter = 0
        for lbl in self.label_names:
            if self.label_input(lbl) == '':
                unlabeled_counter +=1
        return unlabeled_counter == 0


class ReceiptLabel(models.Model):
    """Database class for receipt-level labels"""

    receipt = models.OneToOneField(Receipt, on_delete=models.CASCADE, primary_key=True,
                                   related_name='labels')
    merchant_present = models.BooleanField(default=False)
    merchant_missing = models.BooleanField(default=False)
    merchant_broken = models.BooleanField(default=False)
    amount_present = models.BooleanField(default=False)
    amount_missing = models.BooleanField(default=False)
    amount_broken = models.BooleanField(default=False)
    sub_total_present = models.BooleanField(default=False)
    sub_total_missing = models.BooleanField(default=False)
    sub_total_broken = models.BooleanField(default=False)
    tax_present = models.BooleanField(default=False)
    tax_missing = models.BooleanField(default=False)
    tax_broken = models.BooleanField(default=False)
    date_present = models.BooleanField(default=False)
    date_missing = models.BooleanField(default=False)
    date_broken = models.BooleanField(default=False)
    date_upd = models.DateTimeField(blank=True, null=True, auto_now=True)
    user_upd = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


class Word(models.Model):
    """Database word class"""

    id = models.BigAutoField(primary_key=True)
    receipt = models.ForeignKey(Receipt, models.DO_NOTHING, related_name='words')
    text = models.TextField(blank=True, null=True)
    x1 = models.IntegerField(blank=True, null=True)
    y1 = models.IntegerField(blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    date_add = models.DateTimeField(blank=True, null=True, auto_now_add=True)


class WordLabel(models.Model):
    """Database class for word-level labels"""

    word = models.OneToOneField(Word, on_delete=models.CASCADE, primary_key=True,
                                related_name='labels')
    merchant = models.BooleanField(default=False)
    merchant_rank = models.IntegerField(default=0)
    amount = models.BooleanField(default=False)
    amount_rank = models.IntegerField(default=0)
    sub_total = models.BooleanField(default=False)
    sub_total_rank = models.IntegerField(default=0)
    tax = models.BooleanField(default=False)
    tax_rank = models.IntegerField(default=0)
    date = models.BooleanField(default=False)
    date_rank = models.IntegerField(default=0)
    date_upd = models.DateTimeField(blank=True, null=True, auto_now=True)


# Serializers

class WordLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordLabel
        fields = '__all__'


class ReceiptLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptLabel
        fields = '__all__'


class WordSerializer(serializers.ModelSerializer):

    labels = WordLabelSerializer(many=False, read_only=True, allow_null=True)

    class Meta:
        model = Word
        fields = '__all__'


class ReceiptSerializer(serializers.ModelSerializer):

    words = WordSerializer(many=True, read_only=True, allow_null=True)
    labels = ReceiptLabelSerializer(many=False, read_only=True, allow_null=True)

    class Meta:
        model = Receipt
        fields = '__all__'


def make_chunks(l, n):
    """Helper function that yields successive n-sized chunks from a list"""
    for i in range(0, len(l), n):
        yield l[i:i + n]

