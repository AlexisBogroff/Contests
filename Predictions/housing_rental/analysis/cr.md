
# I. Analysis

## Questions
- more sells than rentals ? (Not good if buy where nothing is rented afterwards)
- Varying distributions of Chambres and Pièces depending on Code Postal? (See with Paris map)


# Further
- Compare with data from other platforms (trends from Seloger might depend form the clients targeted by SeLoger, which are not necessarily representative of the whole IDF clients that sell and rent).
- Compare with previous years (time series)


# II. Build model to predict prix de vente (or Loyer)

## Feature engineering
- create feat 'Paris' (1 when Ville is Paris)
- drop 'Ville'
- return_area = (loyer_area * 12) / prix_de_vente_area
- risk_area = n_announces_loyers_area / n_announces_vente_area
- ratio = return_area / risk_area

## Model
- Train RF on one-hot encoded Code Postal (or hashed)
- Train the model on the whole dataset (train&test), even though it will not be possible to assess its score


## Analysis
- Mesure de performance de modèle R2:
On pourrait mesurer la performance du modèle en comptant le nombre de bonnes réponses si on faisait de la classification, c’est à dire si on prédisait si il s’agit d’un petit appartement (1) ou non (0).

Puisqu’il s’agit d’un problème de régression, on ne peut pas le faire (car une prédiction d’un loyer à) 519€ au lieu du vrai prix 520€ serait considéré comme une mauvaise prédiction - alors qu’on souhaite dire que c’est une bonne prédiction).

Ce que l’on peut faire c’est mesurer à quel point notre prédiction est éloignée de la valeur réelle. On appelle ça une “distance”. On mesure la distance entre notre prédiction et la vraie valeur.
Une mesure de distance courante est la norme d’ordre 2. (Il s’agit juste de l’écart entre 2 points, mis au carré - pour de multiples raisons).

R2 mesure les erreurs de prédiction avec la norm2. R2 mesure plus précisément la variance expliquée par le modèle. C’est à dire que les valeurs réelles varient, et on essaie de trouver des variables qui expliquent cette variance. R2 mesure à quel point nos variables permettent d’expliquer ces variations.


# Further
- Build multiple models, with each being specialised in a market segment (high value good, small goods, Paris expert, etc.)

- Since high values dropped (in superficie, chambres and pièces), a Tree regressor should not be good to extrapolate


# III. Identifier les zones et types de biens intéressants pour de l'investissement locatif

Quelle mesure définirait une opportunité "intéressante" ?
- si ratio Loyer / Prix de vente est élevé

Secteur dynamique :
- si nombre d'achats et de locations élevé
-- bad: peut indiquer que les habitants partent rapidement également
-- good: actifs +liquides

Time series (pas dans la base) :
- si prix d'un bien / quartier augmente au cours du temps
- si prix d'un bien / quartier a baissé avec le covid. Hyp: remontera ensuite
- si loyers augmentent au cours du temps

## Méthodologie

Risk measure:
- si le loyer varie beaucoup pour une même surface, alors c'est plus risqué que si le prix est systématiquement le même pour cette même surface. Ne fonctionne pas car s'il y a trop peu de loyers dans une zone, son risque sera petit.
