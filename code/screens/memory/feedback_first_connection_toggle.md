---
name: first_connection toggle password — champ confirm volontairement masqué
description: Le champ de confirmation dans first_connection reste toujours masqué par choix de sécurité
type: feedback
---

Toggle password dans first_connection.py ne s'applique qu'à `entry_new_password`, jamais à `entry_confirm_password`.

**Why:** Choix délibéré de sécurité : l'utilisateur voit ce qu'il tape dans le premier champ, puis doit ressaisir de mémoire dans le second (toujours masqué). Force la concentration et évite un simple copier-coller visuel.

**How to apply:** Ne pas "corriger" ce comportement comme un bug. C'est une décision UX intentionnelle.
