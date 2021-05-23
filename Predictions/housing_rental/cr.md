
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



# III. Identifier les zones et types de biens intéressants pour de l'investissement locatif

Quelle mesure définirait une opportunité intéressante ?
- si ratio Loyer / Prix de vente est élevé

Secteur dynamique :
- si nombre d'achats et de locations élevé
-- bad: peut indiquer que les habitants partent rapidement également
-- good: actifs +liquides

Time series (pas dans la base) :
- si prix d'un bien / quartier augmente au cours du temps
- si prix d'un bien / quartier a baissé avec le covid. Hyp: remontera ensuite
- si loyers augmentent au cours du temps
