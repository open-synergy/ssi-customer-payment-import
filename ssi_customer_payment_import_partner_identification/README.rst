.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================================================
Customer Payment Import - Partner Identification Matching
=========================================================

This module adds a "Partner Identification" Partner Matching Method to Customer
Payment Import Type. When selected, each import row's paying customer is
resolved by matching a configured column value against ``res.partner.id_number``
(OCA `Partner Identification Numbers
<https://github.com/OCA/partner-contact/tree/14.0/partner_identification>`_) under
a configured identification category, instead of a bank account number.


Work Instruction
================

* `Create Customer Payment Import Type <docs/customer_payment_import_type/index.html>`_


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/ssi-customer-payment-import/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
