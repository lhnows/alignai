import os
from os.path import join
import shutil




if __name__ == '__main__':
    template = open('template.md', 'r').read()
    data = sorted(os.listdir('data'), reverse=True)
    for item in data:
        if item.endswith('.md'):
            shutil.move("data/"+item, "../docs/Arxiv/"+item)  
            
    data = sorted(os.listdir('../docs/Arxiv/'), reverse=True)

    readme_content_template = open('readme_content_template.md', 'r').read()
    readme_content = "\n\n".join(
        [readme_content_template.format(date=item.replace('.md', ''),url=join('Arxiv', item)) for item in data if item.endswith('.md')]
    )
    
   
    markdown = template.format(readme_content=readme_content)
    with open('../docs/Arxiv.md', 'w') as f:
        f.write(markdown)
    
    
