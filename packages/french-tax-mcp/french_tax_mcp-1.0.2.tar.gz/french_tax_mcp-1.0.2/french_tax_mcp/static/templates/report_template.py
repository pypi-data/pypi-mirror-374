# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# or in the 'license' file accompanying this file. This file is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""Report templates for French tax information reports."""

BASE_REPORT_TEMPLATE = """# Rapport Fiscal : {title}

## Vue d'ensemble

{overview}

## Détails

{details}

## Informations pratiques

{practical_info}

## Dates importantes

{important_dates}

## Formulaires

{forms}

---

**Source :** {source}  
**Date de récupération :** {retrieval_date}

> **Avis légal :** Ces informations sont fournies à titre indicatif uniquement et ne constituent pas un conseil fiscal professionnel. Pour des conseils adaptés à votre situation personnelle, veuillez consulter un expert-comptable ou un conseiller fiscal.
"""

TAX_SCHEME_TEMPLATE = """# Dispositif Fiscal : {scheme_name}

## Vue d'ensemble

{overview}

## Avantages fiscaux

{benefits}

## Conditions d'éligibilité

{eligibility}

## Engagements

{commitments}

## Méthode de calcul

{calculation}

## Déclaration

{declaration}

## Dates importantes

{important_dates}

## Formulaires

{forms}

---

**Source :** {source}  
**Date de récupération :** {retrieval_date}

> **Avis légal :** Ces informations sont fournies à titre indicatif uniquement et ne constituent pas un conseil fiscal professionnel. Pour des conseils adaptés à votre situation personnelle, veuillez consulter un expert-comptable ou un conseiller fiscal.
"""

FORM_GUIDE_TEMPLATE = """# Guide du Formulaire : {form_number}

## Description

{description}

## Qui doit remplir ce formulaire ?

{who_should_file}

## Sections principales

{main_sections}

## Cases importantes

{important_boxes}

## Documents justificatifs

{supporting_documents}

## Date limite de dépôt

{deadline}

## Formulaires associés

{related_forms}

---

**Source :** {source}  
**Date de récupération :** {retrieval_date}

> **Avis légal :** Ces informations sont fournies à titre indicatif uniquement et ne constituent pas un conseil fiscal professionnel. Pour des conseils adaptés à votre situation personnelle, veuillez consulter un expert-comptable ou un conseiller fiscal.
"""

CALCULATION_GUIDE_TEMPLATE = """# Guide de Calcul : {calculation_name}

## Description

{description}

## Formule de calcul

{formula}

## Exemple de calcul

{example}

## Paramètres

{parameters}

## Limites et plafonds

{limits}

## Optimisation fiscale

{optimization}

---

**Source :** {source}  
**Date de récupération :** {retrieval_date}

> **Avis légal :** Ces informations sont fournies à titre indicatif uniquement et ne constituent pas un conseil fiscal professionnel. Pour des conseils adaptés à votre situation personnelle, veuillez consulter un expert-comptable ou un conseiller fiscal.
"""

TAX_DEADLINES_TEMPLATE = """# Échéances Fiscales {year}

## Calendrier des échéances

{deadlines_table}

## Déclaration de revenus

{income_declaration}

## Paiement de l'impôt

{tax_payment}

## Autres échéances

{other_deadlines}

---

**Source :** {source}  
**Date de récupération :** {retrieval_date}

> **Avis légal :** Ces informations sont fournies à titre indicatif uniquement et ne constituent pas un conseil fiscal professionnel. Pour des conseils adaptés à votre situation personnelle, veuillez consulter un expert-comptable ou un conseiller fiscal.
"""
