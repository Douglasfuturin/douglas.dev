---
name: invoice-creator
description: Build a clean, send-ready PDF invoice from a few inputs. Math is right, layout is professional, payment instructions are unambiguous. Trigger when the user says "invoice [client] for [amount]," "bill them for the project," "make me an invoice," "send an invoice for last month's work," "generate a PDF invoice," "I need to bill someone," or any variant of needing a paid-on-receipt-grade document with a number on it.
---

# Invoice Builder

Get the user from "I did the work" to "I sent the invoice" in one shot. Right math, clean layout, payment instructions in two places, file named so they can find it again.

## Inputs you need before building

The fewer questions you ask, the better. Build the moment you have these four; ask only what's missing.

| Required | Default if missing | When to ask |
|---|---|---|
| Client name | — | Always required |
| Line items + amounts | — | Always required |
| Issuer (the user's business) | Pull from CLAUDE.md | Ask only if CLAUDE.md is empty |
| Payment method + details | Pull from CLAUDE.md | Ask only if missing |
| Invoice number | Auto-generate `INV-YYYYMMDD-NN` | Never ask |
| Issue date | Today | Never ask |
| Due date | Net 30 from issue date | Ask only if non-standard |
| Currency | USD | Ask only if context suggests otherwise |
| Tax | None | Only include if the user mentioned it |

If the user says "invoice Acme $5,000 for the brand work," you have enough. Build. Don't ask for a tax rate that wasn't mentioned, a PO number that wasn't mentioned, or a billing address you don't have. Bracket missing optional fields and ask at the end.

## Math discipline

Get this wrong once and you destroy the document's authority. Compute and double-check:

```
Line total   = quantity × rate          (per row)
Subtotal     = sum of line totals
Tax          = subtotal × rate          (only if applicable)
Discount     = stated amount or %       (only if applicable, applied before tax)
Total due    = subtotal − discount + tax
Amount paid  = stated                   (only if partial payment received)
Balance due  = total due − amount paid
```

Print intermediate values, not just the total. The recipient should be able to verify the math without a calculator. If a number is rounded, round at the line level using banker's rounding for amounts ending in `.5`, then sum — never sum then round, that introduces visible cents-off errors.

## What the invoice looks like

Two-column header (issuer left, invoice metadata right), a divider, the line items table, a right-aligned totals block, payment instructions full-width, optional notes. Clean, no decorative borders, no logos floating in random places. Default sans-serif body, slightly heavier weight on totals. Currency symbols and amounts right-aligned in the table.

```
┌─────────────────────────────┬─────────────────────────────┐
│ [Issuer business name]      │                    INVOICE  │
│ [Issuer address line 1]     │ Invoice #: INV-20260504-01  │
│ [Issuer address line 2]     │ Date issued: May 4, 2026    │
│ [Issuer email]              │ Date due: June 3, 2026      │
│                             │                             │
│ Bill to:                    │                             │
│ [Client name]               │                             │
│ [Client address / email]    │                             │
└─────────────────────────────┴─────────────────────────────┘

┌────────────────────────────────────────┬─────┬──────────┬──────────┐
│ Description                            │ Qty │ Rate     │ Amount   │
├────────────────────────────────────────┼─────┼──────────┼──────────┤
│ [Line item 1]                          │ 1   │ $X,XXX   │ $X,XXX   │
│ [Line item 2]                          │ 8   │ $XXX     │ $X,XXX   │
└────────────────────────────────────────┴─────┴──────────┴──────────┘

                                                Subtotal   $X,XXX.XX
                                                Tax (X%)   $XXX.XX
                                              ─────────────────────
                                              TOTAL DUE    $X,XXX.XX

Payment terms: Net 30. Late payments accrue 1.5% per month after due date.
Pay by: [Method]
[Account / link / details]

Thank you. Reply to this email with any questions.
```

## How to generate the PDF

Use Python with `reportlab`. It's stable, ships in most Python distributions or installs in one pip command, and produces clean letter-sized PDFs without external services. If `reportlab` isn't available, use `fpdf2` as a fallback. Do not use a headless browser unless the user explicitly wants HTML-to-PDF for branding reasons.

Save to the working directory as:

```
Invoice_[ClientSlug]_[InvoiceNumber].pdf
```

Where `ClientSlug` is the client name lowercased with spaces replaced by hyphens. Example: `Invoice_acme-corp_INV-20260504-01.pdf`.

Use letter size (8.5×11 in) by default; switch to A4 only if the user signals they're outside the US/Canada. Margins: 0.75 in all sides. Body: 11pt. Totals: 12pt bold. Header issuer name: 18pt bold.

If the runtime doesn't have Python, generate a clean HTML version with print-optimized CSS (`@page`) and instruct the user to "Cmd/Ctrl-P → Save as PDF" in their browser.

## What to deliver

After saving the file, give the user a single short summary, one line per fact, and an offer to adjust:

```
Invoice_acme-corp_INV-20260504-01.pdf saved.
Total due: $5,000.00 — net 30 — June 3, 2026.

Want me to adjust the line items, add tax, change payment terms, or set this up as a recurring template?
```

## Recurring invoices

If the user asks to bill the same client on a recurring basis, save a small `invoice-template-[clientslug].md` in the working directory with the issuer block, line items, payment terms, and a comment field for the next invoice number. On the next request you can re-read it instead of re-asking everything.

## Hard rules

- Math is checked twice. Subtotals must equal the sum of line items. Total must equal subtotal − discount + tax. If the totals don't reconcile, do not deliver — fix and re-render.
- Currency formatting matches the locale. `$1,234.56` for USD, `€1.234,56` for EUR, `£1,234.56` for GBP. Use the symbol in the totals; spell out the currency code once in the metadata block (`USD`).
- Never invent payment details. If the user didn't give you bank info, write `[Payment method — to be confirmed by issuer]` and tell them to fill it in before sending. A fake account number on an invoice is worse than a missing one.
- Default to USD and Net 30 only when context gives no other signal. Don't lock those in if the user is clearly working in another currency or industry norm (design Net 15, agencies Net 60, retainers due-on-receipt).
- The invoice must be visually plain — no clipart, no decorative dividers, no inspirational quotes, no thank-you images. The vibe is "auditable document," not "thank-you card."
- Late-payment terms always present. Default: 1.5% per month after due date. Removes ambiguity, gives the user a lever if the client stalls.
- Filename includes both client and invoice number. The user will look for this six months later.
