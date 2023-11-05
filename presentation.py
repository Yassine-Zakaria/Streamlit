import pandas as pd
import plotly.express as px
import pyodbc
import streamlit as st

# La requête SQL pour récupérer les noms et prénoms des étudiants qui ont été présents à tous leurs examens
query1 = '''
SELECT Dim_Etudiants.Nom_Prenom
FROM Dim_Etudiants
INNER JOIN Fact_Table ON Dim_Etudiants.ID_Etudiant = Fact_Table.ID_Etudiant
INNER JOIN Dim_Examens ON Fact_Table.ID_Matiere = Dim_Examens.ID_Matiere
INNER JOIN Dim_Acces ON Fact_Table.ID_Matiere = Dim_Acces.ID_Acces
GROUP BY Dim_Etudiants.Nom_Prenom
HAVING COUNT(DISTINCT Fact_Table.ID_Matiere) = COUNT(DISTINCT Dim_Acces.ID_Acces);
'''

# La requête SQL pour récupérer le taux de réussite pour chaque matière
query2 = '''
SELECT Dim_Examens.Matiere, AVG(Fact_Table.ID_Matiere) AS Taux_reussite
FROM Fact_Table
INNER JOIN Dim_Examens ON Fact_Table.ID_Matiere = Dim_Examens.ID_Matiere AND Fact_Table.ID_Matiere = Dim_Examens.Note
GROUP BY Dim_Examens.Matiere;
'''

# La requête SQL pour récupérer les noms et prénoms des étudiants qui ont obtenu une note supérieure à la moyenne de leur niveau
query3 = '''
SELECT Dim_Etudiants.Nom_Prenom, Dim_Examens.Matiere, Moyenne_niveau
FROM Fact_Table
INNER JOIN Dim_Etudiants ON Fact_Table.ID_Etudiant = Dim_Etudiants.ID_Etudiant
INNER JOIN Dim_Examens ON Fact_Table.ID_Matiere = Dim_Examens.ID_Matiere
INNER JOIN (SELECT Dim_Etudiants.Niveau, AVG(Fact_Table.ID_Matiere) AS Moyenne_niveau
            FROM Fact_Table
            INNER JOIN Dim_Etudiants ON Fact_Table.ID_Etudiant = Dim_Etudiants.ID_Etudiant
            INNER JOIN Dim_Examens ON Fact_Table.ID_Etudiant = Dim_Examens.Note
            GROUP BY Dim_Etudiants.Niveau) AS Moyennes_par_niveau
ON Dim_Etudiants.Niveau = Moyennes_par_niveau.Niveau
WHERE Fact_Table.ID_Matiere > Moyenne_niveau order by Moyenne_niveau;
'''

# Connexion à la base de données SQL Server
conn = pyodbc.connect('Driver={SQL Server};''Server=YASSINE;''Database=destination;''Trusted_Connection=yes;')

with conn.cursor() as cursor:
    df1 = pd.read_sql_query(query1, conn)
    df2 = pd.read_sql_query(query2, conn)
    df3 = pd.read_sql_query(query3, conn)

# Fermer la connexion à la base de données
conn.close()

# Création des graphiques

# Graphique 1
fig1 = px.bar(df1, x='Nom_Prenom', color='Nom_Prenom')

# Graphique 2
fig2 = px.bar(df2, x='Matiere', y='Taux_reussite', color='Matiere', color_discrete_sequence=px.colors.qualitative.Safe)

# Graphique 3 en scatterplot
fig3 = px.scatter(df3, x='Nom_Prenom', y='Moyenne_niveau', color='Matiere')

fig3.update_layout(
    title='Graphique 3: Notes des étudiants supérieures à la moyenne de leur niveau',
    xaxis_title="Nom et prénom de l'étudiant",
    yaxis_title="Pourcentage",
    legend_title="Matière",
    width=1000
)
fig3.update_traces(texttemplate='%{y:.2s}')

# Affichage des graphiques avec Streamlit
st.title('Résultats de l\'analyse graphique')

def Explication():
    st.header("Explication des graphiques!")
    st.write("Compréhension des graphiques générés à partir de données hétérogènes.")
    st.write("Quel graphique voulez-vous comprendre?")
    choix = st.selectbox(" ", ["Les étudiants qui ont assisté à tous leurs examens", "Le taux de réussite pour chaque matière", "Les étudiants qui ont obtenu une note supérieure à la moyenne de leur niveau"])

    if choix == "Les étudiants qui ont assisté à tous leurs examens":
        #st.header('Graphique 1: Étudiants ayant été présents à tous leurs examens')
        st.write("Ce graphique montre les noms et prénoms des étudiants qui ont assisté à tous leurs examens.")
        st.plotly_chart(fig1)

    elif choix == "Le taux de réussite pour chaque matière":
        st.header('Graphique 2: Taux de réussite pour chaque matière')
        st.write("Ce graphique montre le taux de réussite moyen pour chaque matière.")
        st.plotly_chart(fig2)

    elif choix == "Les étudiants qui ont obtenu une note supérieure à la moyenne de leur niveau":
        st.header('Graphique 3: Notes des étudiants supérieures à la moyenne de leur niveau')
        st.write("Ce graphique montre les noms et prénoms des étudiants qui ont obtenu une note supérieure à la moyenne de leur niveau, pour chaque matière.")
        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.write("Veuillez sélectionner un choix valide.")

Explication()
