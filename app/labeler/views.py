import json
import os

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import *
from app.settings import RECEIPT_IMG_PATH


@login_required
def index(request):
    """Function that generates receipt list view"""

    # Extract url params
    q = request.GET.get('q')
    page = request.GET.get('page')

    # Apply search query filter
    if q is not None:
        receipt_list = Receipt.objects.filter(
            Q(id__contains=q) | Q(receipt_code__icontains=q)).order_by('id')
    else:
        receipt_list = Receipt.objects.order_by('id')

    if not request.user.is_staff:
        receipt_list = receipt_list.filter(shoebox__user__id=request.user.id)

    # Add pagination
    paginator = Paginator(receipt_list, 50)

    # Build template context
    context = {
        'receipt_list': paginator.get_page(page),
        'q': q,
        'page': page,
        'url_filters': make_url_filters(request),
    }

    # Render web page and return
    return render(request, 'labeler/index.html', context)


@login_required
def receipt_view(request, receipt_id):
    """Function that generates individual receipt view"""

    # Error messages are not generated at the moment (TBD)
    messages = []
    label_msg_success = "Labels successfully saved. Thank you!"

    # Process form submission first
    if request.method == 'POST':
        receipt = get_object_or_404(Receipt, pk=receipt_id)
        # Clean all labels from receipt
        # NG if there is an error in code below, efficient though
        receipt.clean_labels()
        if not hasattr(receipt, 'labels'):
            receipt.labels = ReceiptLabel()
        # Iterate thru labels
        for param in request.POST:
            if param.endswith('_selection'):
                lbl = param.replace('_selection', '')
                # Get list of word ids marked as labels (their format is string)
                wids = request.POST.get(param, '').split('|')

                for i, wid in enumerate(wids):
                    # Skip empty params
                    if wid == '':
                        continue
                    # Missing label
                    if wid == 'm':
                        setattr(receipt.labels, lbl+'_missing', True)
                        continue
                    # Broken label
                    elif wid == 'b':
                        setattr(receipt.labels, lbl + '_broken', True)
                        continue
                    # Invalid ids - simply skip
                    try:
                        int(wid)
                    except:
                        continue
                    if int(wid) < 1:
                        continue
                    # Process proper ids
                    try:
                        word = Word.objects.get(id=int(wid))
                    except Word.DoesNotExist:
                        # TBD: treat exceptions here properly
                        continue
                    else:
                        # Set word labels
                        if not hasattr(word, 'labels'):
                            word.labels = WordLabel()
                        setattr(word.labels, lbl, True)
                        setattr(word.labels, lbl+'_rank', i+1)
                        word.labels.save()
                        # Set receipt labels
                        setattr(receipt.labels, lbl+'_present', True)

        # Save receipt labels
        receipt.labels.receipt_id = receipt.id
        receipt.labels.user_upd = request.user
        receipt.labels.save()
        messages.append({'type': 'success', 'content': label_msg_success})

    # Extract url params
    q = request.GET.get('q')
    page = request.GET.get('page')

    # Get receipt object anew
    receipt = get_object_or_404(Receipt, pk=receipt_id)

    # Get all receipts filtered by search query (if applicable)
    if q is not None:
        receipts = Receipt.objects.filter(
            Q(id__contains=q) | Q(receipt_code__icontains=q)).order_by('id').all()
    else:
        receipts = Receipt.objects.order_by('id').all()

    # Get ids of next and previous receipt for navigation
    next_id = None
    prev_id = None
    for i, r in enumerate(receipts):
        if r.id == receipt_id:
            if i < len(receipts) - 1:
                next_id = receipts[i + 1].id
            if i > 0:
                prev_id = receipts[i - 1].id

    # Serialize objects for front-end javascript
    receipt_json_alt = json.dumps(ReceiptSerializer(receipt).data)

    # Make list of assigned words. Used by front-end js code
    assigned = {
        'merchant': None,
        'amount': None,
        'sub_total': None,
        'tax': None,
        'date': None}
    for lbl in assigned:
        words = receipt.words.filter(**{'labels__' + lbl: True}).all()
        assigned[lbl] = [word.id for word in words]

    # Build url of receipt image
    receipt_image_name = str(receipt.id) + '_' + receipt.receipt_code + '.png'
    receipt_image_url = os.path.join(RECEIPT_IMG_PATH, receipt_image_name)

    # Build template context
    context = {
        'receipt': receipt,
        'receipt_json': receipt_json_alt,
        'assigned_json': json.dumps(assigned),
        'prev_id': prev_id,
        'next_id': next_id,
        'q': q,
        'page': page,
        'url_filters': make_url_filters(request),
        'messages': messages,
        'receipt_image_url': receipt_image_url,
    }

    # Render and return page
    return render(request, 'labeler/receipt.html', context)


def make_url_filters(request):
    """Function that produces url parameters concatenated into a string"""
    # Extract url params
    q = request.GET.get('q')
    page = request.GET.get('page')
    # Filters
    url_params = {}
    if (q is not None) and (q != ""):
        url_params['q'] = q
    if (page is not None) and (int(page) > 0):
        url_params['page'] = int(page)

    url_filters = {}
    url_filters['all'] = "&".join([f"{pair[0]}={pair[1]}" for pair in url_params.items()])

    return url_filters
