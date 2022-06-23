import xml.etree.ElementTree as ET
import glob
from datetime import date
import pandas as pd
from qualis import get_qualis

present_year = date.today().year


def parse_xml_lattes(xml_file):
    """
     ---> This function parses LATTES curricula in xml format
    :param xml_file:
    :return: it returns a dictionary containing the name and elements from module xml.etree.ElementTree
    for articles, books and book chapters
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    get_name = root.findall('./DADOS-GERAIS')
    name = get_name[0].attrib['NOME-COMPLETO']
    books = dict()
    chapters = dict()
    articles = root.findall('./PRODUCAO-BIBLIOGRAFICA/ARTIGOS-PUBLICADOS/ARTIGO-PUBLICADO')
    # checking for books and book chapters
    check4books = root.findall('./PRODUCAO-BIBLIOGRAFICA/')
    published_books = False
    chapters_published = False
    for book in check4books:
        if book.tag == 'LIVROS-E-CAPITULOS':
            books_and_chapters = root.findall('./PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/')
            for item in books_and_chapters:
                if item.tag == 'LIVROS-PUBLICADOS-OU-ORGANIZADOS':
                    published_books = True
                if item.tag == 'CAPITULOS-DE-LIVROS-PUBLICADOS':
                    chapters_published = True
    if published_books == True:
        books = root.findall('./PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/LIVROS-PUBLICADOS-OU-ORGANIZADOS/')
    if chapters_published == True:
        chapters = root.findall('./PRODUCAO-BIBLIOGRAFICA/LIVROS-E-CAPITULOS/CAPITULOS-DE-LIVROS-PUBLICADOS/')

    records = {
        'name': name,
        'articles': articles,
        'books': books,
        'chapters': chapters
    }
    return records


def format_auhors(list_of_authors):
    citation_name = list()
    for name in list_of_authors:
        get_name = list()
        list_of_names = name.split(' ')
        lengh_name = len(list_of_names)
        if ',' in list_of_names[0]:
            last_name = list_of_names[0]
            list_of_names.remove(last_name)
            last_name = last_name.replace(',', '')
            list_of_names.append(last_name)
        get_name.append(list_of_names[-1] + ', ')
        for k, elm in enumerate(list_of_names):
            if k < lengh_name - 1 and elm != 'DE' and elm != 'DA':
                try:
                    get_name.append(elm[0] + '.')
                except IndexError:
                    print('ERROR: IndexError: string index out of range')
        get_name = ' '.join(get_name)
        citation_name.append(get_name)
    citation_name = '; '.join(citation_name)
    return citation_name


def get_articles(records, y_start=present_year - 5, y_end=present_year):
    compiled_articles = list()
    for art in records['articles']:
        year = int(art[0].attrib['ANO-DO-ARTIGO'])
        if y_start <= year <= y_end:
            title = art[0].attrib['TITULO-DO-ARTIGO']
            journal = art[1].attrib['TITULO-DO-PERIODICO-OU-REVISTA']
            issn = art[1].attrib['ISSN']
            issn = issn[:4] + '-' + issn[4:]  # re formating the ISSN to be used in get_qualis_function
            qualis = get_qualis(issn)
            volume = art[1].attrib['VOLUME']
            issue = art[1].attrib['FASCICULO']
            page_init = art[1].attrib['PAGINA-INICIAL']
            page_end = art[1].attrib['PAGINA-FINAL']
            # print(f'{first_author}, {year}, {title}, {journal}, {volume}, {number}, {page_init}, {page_end}')
            authors = list()
            a_index = 2
            while a_index >= 2:
                try:
                    author = art[a_index].attrib['NOME-COMPLETO-DO-AUTOR']
                    authors.append(author.upper().replace("'", ''))
                    a_index += 1
                except KeyError:
                    break
                except IndexError:
                    break
            authors = format_auhors(authors)
            # print(f'{journal}, {volume}({fasc}): {page_init}-{page_end}')
            article_data = {
                'authors': authors,
                'year': year,
                'title': title,
                'journal': journal,
                'issn': issn,
                'qualis': qualis,
                'volume': volume,
                'issue': issue,
                'first_page': page_init,
                'last_page': page_end
            }
            compiled_articles.append(article_data)
    return compiled_articles


def get_books(records, y_start=present_year - 5, y_end=present_year):
    compiled_books = list()
    for book in records['books']:
        year = int(book[0].attrib['ANO'])
        if y_start <= year <= y_end:
            title = book[0].attrib['TITULO-DO-LIVRO']
            type = book[0].attrib['NATUREZA']
            if type == 'NAO_INFORMADO':
                type = 'no data'
            release = book[0].attrib['MEIO-DE-DIVULGACAO']
            if release == 'NAO_INFORMADO':
                release = 'no data'
            n_pages = book[1].attrib['NUMERO-DE-PAGINAS']
            editor = book[1].attrib['NOME-DA-EDITORA']
            isbn = book[1].attrib['ISBN']
            if not isbn:
                isbn = 'no data'
            # first_author = book[2].attrib['NOME-COMPLETO-DO-AUTOR']
            # print(f'{first_author}, {year}, {title}, {n_pages}, {isbn}, {type}, {release}')
            authors = list()
            a_index = 2
            while a_index >= 2:
                try:
                    author = book[a_index].attrib['NOME-COMPLETO-DO-AUTOR']
                    authors.append(author.upper().replace("'", ''))
                    a_index += 1
                except KeyError:
                    break
                except IndexError:
                    break
            authors = format_auhors(authors)
            book_data = {
                'authors': authors,
                'year': year,
                'title': title,
                'editor': editor,
                'n_pages': n_pages,
                'isbn': isbn,
                'type': type,
                'release': release
            }
            compiled_books.append(book_data)
    return compiled_books


def get_chapters(records, y_start=present_year - 5, y_end=present_year):
    compiled_chapters = list()
    for chapter in records['chapters']:
        year = int(chapter[0].attrib['ANO'])
        if y_start <= year <= y_end:
            title_chapter = chapter[0].attrib['TITULO-DO-CAPITULO-DO-LIVRO']
            type = chapter[0].attrib['TIPO']
            release = chapter[0].attrib['MEIO-DE-DIVULGACAO']
            title_book = chapter[1].attrib['TITULO-DO-LIVRO']
            page_init = chapter[1].attrib['PAGINA-INICIAL']
            page_end = chapter[1].attrib['PAGINA-FINAL']
            org = chapter[1].attrib['ORGANIZADORES']
            editor = chapter[1].attrib['NOME-DA-EDITORA']
            isbn = chapter[1].attrib['ISBN']
            if not isbn:
                isbn = 'no data'
            authors = list()
            a_index = 2
            while a_index >= 2:
                try:
                    author = chapter[a_index].attrib['NOME-COMPLETO-DO-AUTOR']
                    authors.append(author.upper().replace("'", ''))
                    a_index += 1
                except KeyError:
                    break
                except IndexError:
                    break
                except TypeError:
                    break
            authors = format_auhors(authors)
            chapter_data = {
                'authors': authors,
                'year': year,
                'title_chapter': title_chapter,
                'title_book': title_book,
                'page_init': page_init,
                'page_end': page_end,
                'editor': editor,
                'org': org,
                'type': type,
                'release': release,
                'isbn': isbn
            }
            compiled_chapters.append(chapter_data)
    return compiled_chapters


def compile_bibliography(lattes_xml_file, y_start=present_year - 5, y_end=present_year):
    records = parse_xml_lattes(lattes_xml_file)
    compiled_articles = get_articles(records, y_start, y_end)
    compiled_books = get_books(records, y_start, y_end)
    compiled_chapters = get_chapters(records, y_start, y_end)
    return [compiled_articles, compiled_books, compiled_chapters]


def main(lattes_list):
    n_lattes = len(lattes_list)
    compiled_articles_pd = pd.DataFrame()
    compiled_books_pd = pd.DataFrame()
    compiled_chapters_pd = pd.DataFrame()
    for idx, lattes in enumerate(lattes_list):
        compiled_articles, compiled_books, compiled_chapters = compile_bibliography(lattes)
        if n_lattes == 1:
            compiled_articles_pd = pd.DataFrame(compiled_articles)
            compiled_books_pd = pd.DataFrame(compiled_books)
            compiled_chapters_pd = pd.DataFrame(compiled_chapters)
            xlsx_file = lattes.replace('.xml', '.xlsx')
            with pd.ExcelWriter(xlsx_file, engine='xlsxwriter') as lattes:
                compiled_articles_pd.to_excel(lattes, sheet_name='articles', index=False)
                compiled_books_pd.to_excel(lattes, sheet_name='books', index=False)
                compiled_chapters_pd.to_excel(lattes, sheet_name='chapters', index=False)
        elif n_lattes > 1:
            xlsx_file = 'compiled_lattes.xlsx'
            if idx == 0:
                print('initiating dataframe', lattes)
                compiled_articles_pd = pd.DataFrame(compiled_articles)
                compiled_books_pd = pd.DataFrame(compiled_books)
                compiled_chapters_pd = pd.DataFrame(compiled_chapters)
            if 0 < idx < n_lattes - 1:
                print('appendink to dataframe', lattes)
                try:
                    compiled_articles_pd = compiled_articles_pd.append(compiled_articles, ignore_index=True)
                    compiled_books_pd = compiled_books_pd.append(compiled_books, ignore_index=True)
                    compiled_chapters_pd = compiled_chapters_pd.append(compiled_chapters, ignore_index=True)
                except IndexError:
                    print(IndexError)
            if idx == n_lattes - 1:
                print('writing dataframe', lattes)
                try:
                    compiled_articles_pd = compiled_articles_pd.append(compiled_articles, ignore_index=True)
                    compiled_books_pd = compiled_books_pd.append(compiled_books, ignore_index=True)
                    compiled_chapters_pd = compiled_chapters_pd.append(compiled_chapters, ignore_index=True)
                except IndexError:
                    print(IndexError)
                # sorting and removing duplicates
                compiled_articles_pd.sort_values('year', inplace=True)
                compiled_articles_pd.drop_duplicates(subset='title', inplace=True)
                compiled_books_pd.sort_values('year', inplace=True)
                compiled_books_pd.drop_duplicates(subset='title', inplace=True)
                compiled_chapters_pd.sort_values('year', inplace=True)
                compiled_chapters_pd.drop_duplicates(subset='title_book', inplace=True)
                with pd.ExcelWriter(xlsx_file, engine='xlsxwriter') as lattes:
                    compiled_articles_pd.to_excel(lattes, sheet_name='articles', index=False)
                    compiled_books_pd.to_excel(lattes, sheet_name='books', index=False)
                    compiled_chapters_pd.to_excel(lattes, sheet_name='chapters', index=False)
        else:
            print('The is no LATTES to process')


if __name__ == "__main__":
    # lattes_list = [
    #     'ricardo_pinto_da_rocha.xml',
    #     'renata_pardini.xml',
    #     'daniel_lahr.xml',
    #     'fernando_marques.xml',
    #     'antonio_carlos_marques.xml'
    # ]
    dir_path = r'./lattes/*.xml'
    lattes_list = list_of_lattes = glob.glob(dir_path, recursive=True)
    main(lattes_list)
