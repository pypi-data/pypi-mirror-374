# Xebus Eduka SIS Connector
Connector to fetch data from a school's Eduka information system.

```csv
"Code identifiant";"Nom";"Prénom";"Nom complet";"Nationalité 1";"Langue maternelle";"Date de naissance";"Age";"Branche scolaire";"Classe";"Code identifiant R1";"Code identifiant R2";"Prénom R1";"Prénom R2";"Nom R1";"Nom R2";"Nom complet R1";"Nom complet R2";"Langue(s) parlée(s) R1";"Langue(s) parlée(s) R2";"Nationalité(s) R1";"Nationalité(s) R2";"Adresse e-mail R1";"Adresse e-mail R2";"Téléphone mobile R1";"Téléphone mobile R2";"Street R1";"Street R2"
"12046S3485";"CAUNE NGUYEN";"Éline Xuân Anh Aurora";"CAUNE NGUYEN Éline Xuân Anh Aurora";"French";"Vietnamese";"23/12/2016";"7";"Elementaire » Cours élémentaire 1 (Ce1)";"CE1 B";"12046G3483";"12046G3482";"Thi Thanh Truc";"Daniel";"NGUYEN";"CAUNE";"NGUYEN Thi Thanh Truc";"CAUNE Daniel";"French, English, Vietnamese";"French, English, Vietnamese";"Vietnamese";"French";"thithanhtruc.nguyen@gmail.com";"daniel.caune@gmail.com";"+84 822 170 781";"+84 812 170 781";"18A Võ Trường Toản, P. An Phú, Quận 2, TP.HCM";"18A Võ Trường Toản, P. An Phú, Quận 2, TP.HCM"
```

List of the CSV fields:

Section **Child**

| Eduka Field Name  | Description                                                                                           | Xebus Field Name |
|-------------------|-------------------------------------------------------------------------------------------------------|------------------|
| Code identifiant  | The child’s unique identifier as referenced in the school organization’s information system (SIS).    | SIS ID           |
| Prénom            | The given name of the child.                                                                          | First Name       |
| Nom               | The surname of the child.                                                                             | Last Name        |
| Nom complet       | The complete personal name of the child, including their last name, first name and middle name(s).    | Full Name        |
| Langue maternelle | The spoken language of the child.                                                                     | Language         |
| Nationalité 1     | The primary nationality of the child.                                                                 | Nationality      |
| Date de naissance | The date of birth of the child, in the format `DD/MM/YYYY`.                                           |                  | Date of Birth    |
| Branche scolaire  | The name of the education grade that the child has reached for the current or the coming school year. | Grade Name       |
| Classe            | The name of the class that the child has enrolled for the current or the coming school year.          | Class Name       |

Section **Primary Parent**

| Eduka Field Name       | Description                                                                                                 | Xebus Field Name |
|------------------------|-------------------------------------------------------------------------------------------------------------|------------------|
| Code identifiant R1    | The primary parent’s unique identifier as referenced in the school organization’s information system (SIS). | SIS ID           |
| Prénom R1              | The first name (also known as the given name) of the primary parent.                                        | First Name       |
| Nom R1                 | The surname of the primary parent.                                                                          | Last Name        |
| Nom complet R1         | The complete personal name of the primary parent, including their surname, first name and middle name(s).   | Full Name        |
| Langue(s) parlée(s) R1 | The preferred language of the primary parent.                                                               | Language         |
| Nationalité(s) R1      | The primary nationality of the primary parent.                                                              | Nationality      |
| Adresse e-mail R1      | The email address of the primary parent.                                                                    | Email Address    |
| Téléphone mobile R1    | The international mobile phone number of the primary parent.                                                | Phone Number     |
| Street R1              | The address of the home where the primary parent accommodates their child.                                  | Home Address     |

Section **Secondary Parent**

| Eduka Field Name       | Description                                                                                                   | Xebus Field Name |
|------------------------|---------------------------------------------------------------------------------------------------------------|------------------|
| Code identifiant R2    | The secondary parent’s unique identifier as referenced in the school organization’s information system (SIS). | SIS ID           |
| Prénom R2              | The first name (also known as the given name) of the secondary parent.                                        | First Name       |
| Nom R2                 | The surname of the secondary parent.                                                                          | Last Name        |
| Nom complet R2         | The complete personal name of the secondary parent, including their surname, first name and middle name(s).   | Full Name        |
| Langue(s) parlée(s) R2 | The preferred language of the secondary parent.                                                               | Language         |
| Nationalité(s) R2      | The primary nationality of the secondary parent.                                                              | Nationality      |
| Adresse e-mail R2      | The email address of the secondary parent.                                                                    | Email Address    |
| Téléphone mobile R2    | The international mobile phone number of the secondary parent.                                                | Phone Number     |
| Street R2              | The address of the home where the secondary parent accommodates their child.                                  | Home Address     |


## Languages & Nationalities

We provide the list of language names and nationality names and their respective ISO codes as CSV files in the folder `data` of this library.  We assume that these are the same for all instances of the Eduka platform used by school organizations.  The library loads these lists by default when the client application does not explicitly pass these mappings. 


## Grade Names

We do not provide a list of educational grade level names, as it appears that school organizations define their own names.

_Note: For the purpose of testing our library, we provide a list of educational grade level names `grades_names.csv`, located in the root path of our library project, but this list is not distributed with our library._
