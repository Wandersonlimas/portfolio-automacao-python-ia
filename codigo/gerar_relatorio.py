"""Relatório vetorial executivo do Case 02 com números derivados do ETL."""
from __future__ import annotations
import math
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from insights import gerar_insights

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('DV',FONT));pdfmetrics.registerFont(TTFont('DV-B',FONT_BOLD))
W,H=A4; NAVY=HexColor('#102536'); MINT=HexColor('#46D5B9'); TEAL=HexColor('#0D927D')
PAPER=HexColor('#F2F6F8'); WHITE=HexColor('#FFFFFF'); MUTED=HexColor('#688091'); LINE=HexColor('#DCE8ED'); RED=HexColor('#A94F50')


def text(c,x,y,t,size=10,color=NAVY,bold=False):
    c.setFillColor(color);c.setFont('DV-B' if bold else 'DV',size);c.drawString(x,y,str(t))


def wrap(c,raw,x,y,maxw,size=9,leading=15,color=MUTED,font='DV',maxlines=30):
    c.setFillColor(color);c.setFont(font,size)
    for paragraph in str(raw).split('\n'):
        words=paragraph.split(); ln=''
        for word in words:
            prop=(ln+' '+word).strip()
            if pdfmetrics.stringWidth(prop,font,size)>maxw and ln:
                c.drawString(x,y,ln);y-=leading;ln=word;maxlines-=1
            else:ln=prop
            if maxlines<=0:return y
        c.drawString(x,y,ln);y-=leading;maxlines-=1
        if maxlines<=0:return y
    return y


def label(c,x,y,t):text(c,x,y,t.upper(),8.5,TEAL,True)


def background(c,title,page,dark=False):
    c.setFillColor(NAVY if dark else PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
    if not dark:
        c.setFillColor(WHITE);c.roundRect(28,45,W-56,H-89,17,fill=1,stroke=0)
        c.setStrokeColor(LINE);c.setLineWidth(.8);c.line(49,H-85,W-49,H-85)
        label(c,49,H-66,'PORTFÓLIO TÉCNICO / AUTOMAÇÃO COM PYTHON')
        text(c,49,25,'WANDERSON LIMAS  ·  DADOS 100% SINTÉTICOS',7.7,MUTED,True)
        text(c,W-97,25,f'{page} / 04',7.8,MUTED)
        text(c,49,H-119,title,19,NAVY,True)
    else:
        c.setFillColor(HexColor('#133A45')); c.circle(W+12,82,270,fill=1,stroke=0)
        c.setStrokeColor(HexColor('#1C6F6A'));c.setLineWidth(1.5)
        for j in range(8): c.line(345+j*32,270,370+j*25,270+j*32)


def rectcard(c,x,y,w,h,caption,value,foot=''):
    c.setFillColor(WHITE);c.setStrokeColor(LINE);c.roundRect(x,y,w,h,13,fill=1,stroke=1)
    text(c,x+13,y+h-23,caption.upper(),7.3,MUTED,True)
    text(c,x+13,y+h-56,value,18,NAVY,True)
    if foot:wrap(c,foot,x+13,y+23,w-26,size=7.4,leading=10,maxlines=2)


def section(c,x,y,title,body,w=490):
    label(c,x,y,title)
    return wrap(c,body,x,y-18,w,size=9.5,leading=16,color=MUTED)


def relatorio(raiz: Path,dados: dict)->Path:
    raiz=Path(raiz);dest=raiz/'entregaveis'/'Relatorio_Executivo_Automacao_Python_IA.pdf'
    dest.parent.mkdir(exist_ok=True,parents=True)
    c=canvas.Canvas(str(dest),pagesize=A4,pageCompression=1)
    c.setTitle('Automação de operações multicanal | Case técnico Python + IA opcional')
    c.setAuthor('Wanderson Limas | Portfólio demonstrativo com dados sintéticos')
    k=dados['kpis'];q=dados['qualidade'];mensais=dados['series']['mensais']
    motivos=sorted(k['motivos_excecao'].items(),key=lambda x:-x[1]);analises=gerar_insights(k,mensais)
    # 1: Capa
    background(c,'',1,True)
    text(c,52,H-75,'WANDERSON LIMAS',12,MINT,True)
    text(c,52,H-113,'PORTFÓLIO TÉCNICO  /  CASE 02',8.6,HexColor('#A5C6D0'),True)
    text(c,52,H-214,'AUTOMAÇÃO',35,WHITE,True)
    text(c,52,H-262,'DE OPERAÇÕES',35,WHITE,True)
    text(c,52,H-310,'MULTICANAL.',35,MINT,True)
    wrap(c,'ETL em Python · Validação de dados · Conciliação · SLA · Relatórios · Integração opcional com IA',52,H-365,440,size=12.4,leading=22,color=HexColor('#C3D6DA'),maxlines=4)
    c.setStrokeColor(MINT);c.setLineWidth(3);c.line(52,H-444,175,H-444)
    text(c,52,183,'3 FONTES',15,WHITE,True);text(c,52,165,'Pedidos · Pagamentos · Expedições',9,HexColor('#C2D6D9'))
    text(c,52,112,'ESTUDO 100% SINTÉTICO',11,MINT,True)
    wrap(c,'Caso demonstrativo criado para avaliação técnica. Indicadores, exceções e narrativa não representam entregas ou resultados reais de qualquer empresa.',52,88,420,8.6,13,HexColor('#C3D5DC'),maxlines=3)
    c.showPage()
    # 2: Executivo
    background(c,'Resumo executivo',2)
    gap=11;left=49;cw=(W-98-gap)/2;top=H-152;ch=89
    rectcard(c,left,top-ch,cw,ch,'Pedidos válidos',f"{k['pedidos_validos']:,}".replace(',','.'),'Após a quarentena de registros inválidos')
    rectcard(c,left+cw+gap,top-ch,cw,ch,'Exceções por pedido',f"{k['taxa_excecao_pct']:.1f}%".replace('.',','),'Pedidos com ao menos uma regra acionada')
    rectcard(c,left,top-2*ch-gap,cw,ch,'SLA de expedição',f"{k['sla_pct']:.1f}%".replace('.',','),'No prazo / pedidos efetivamente despachados')
    rectcard(c,left+cw+gap,top-2*ch-gap,cw,ch,'Valor conciliado',f"R$ {k['receita_conciliada_centavos']/100:,.2f}".replace(',','X').replace('.',',').replace('X','.'),'Base fictícia, sem impostos ou devoluções')
    y=top-2*ch-gap-39
    label(c,left,y,'Volume de registros válidos por mês')
    maxv=max(z['pedidos'] for z in mensais);ax_y=y-176;barW=96;start=left+41
    for i,m in enumerate(mensais):
        v=m['pedidos'];h=148*v/maxv;x=start+i*142
        c.setFillColor(HexColor('#EAF3F3'));c.roundRect(x,ax_y,barW,150,7,fill=1,stroke=0)
        c.setFillColor(TEAL);c.roundRect(x,ax_y,barW,h,7,fill=1,stroke=0)
        text(c,x+24,ax_y+h+8,f'{v:,}'.replace(',','.'),10,NAVY,True)
        text(c,x+20,ax_y-18,m['chave'],9,MUTED,True)
    y=ax_y-61
    section(c,left,y,'O que o pipeline entrega',
      'Padronização de três fontes, identificação de registros inválidos, conciliação entre pedido e pagamento, controle de expedição, trilha CSV das exceções, dashboard offline e relatório executivo.',W-98)
    section(c,left,y-94,'Interpretação responsável',
      'Números sintéticos. Redução de esforço, economia, ganho de produtividade e impacto financeiro NÃO foram medidos. O estudo demonstra mecanismo técnico, não resultados reais.',W-98)
    c.showPage()
    # 3: Diagnósticos
    background(c,'Leitura analítica e exceções',3)
    y=H-160
    for i,(motivo,contagem) in enumerate(motivos[:5]):
        text(c,49,y,motivo,9.5,NAVY,True)
        text(c,W-104,y,str(contagem),10,TEAL,True)
        w=(W-146)*contagem/max(1,motivos[0][1]);c.setFillColor(HexColor('#EDF4F6'));c.roundRect(49,y-22,W-147,11,5,fill=1,stroke=0)
        c.setFillColor(TEAL if i==0 else HexColor('#77BBAE'));c.roundRect(49,y-22,w,11,5,fill=1,stroke=0)
        y-=60
    y-=9
    c.setFillColor(HexColor('#E7F6F1'));c.roundRect(45,y-178,W-90,167,11,fill=1,stroke=0)
    label(c,58,y-29,'Diagnóstico reprodutível / regras, não IA')
    yy=y-51
    for i,a in enumerate(analises):
        text(c,58,yy,f'{i+1:02d}. {a["titulo"]}',8.3,NAVY,True)
        yy=wrap(c,a['texto'],65,yy-14,W-145,size=7.8,leading=11,maxlines=3)-8
    section(c,49,y-210,'Evidências disponíveis',
      'O repositório inclui CSV original, linhas rejeitadas, pedidos processados, exceções individualizadas, JSON consolidado e testes automatizados. Cada indicador do painel é recalculado nos filtros.',W-98)
    c.showPage()
    # 4: Método
    background(c,'Arquitetura, fórmulas e limites',4)
    label(c,49,H-157,'Fluxo automatizado')
    steps=['01  Ingestão CSV','02  Quarentena','03  Conciliação','04  KPIs + PDF','05  IA opcional']
    sy=H-235
    for i,s in enumerate(steps):
        x=49+(i%3)*168;y=sy-(i//3)*76
        c.setFillColor(HexColor('#F3F9F9'));c.setStrokeColor(LINE);c.roundRect(x,y,156,61,10,fill=1,stroke=1)
        text(c,x+9,y+26,s,8.7,NAVY,True)
    y=H-402
    section(c,49,y,'Taxa de exceção','Pedidos válidos com uma ou mais ocorrências / total de pedidos válidos. Pedidos duplicados e inválidos são excluídos antes do cálculo.',W-98)
    section(c,49,y-83,'SLA de expedição','Pedidos com pagamento confirmado e expedição válida em até 48 horas / total de pedidos confirmados efetivamente despachados. Sem expedição é exceção separada.',W-98)
    section(c,49,y-166,'Valor conciliado','Soma do valor dos pedidos com pagamento confirmado e sem divergência de valor. Não representa receita contábil, DRE ou resultado econômico.',W-98)
    section(c,49,y-249,'Integração opcional com IA','Código de integração com a Responses API disponível. Exige configuração explícita de chave e modelo, envia apenas agregados fictícios e não faz parte da execução padrão. Nenhuma análise gerada por LLM foi apresentada como já realizada.',W-98)
    c.save();return dest

if __name__=='__main__':
    import json
    raiz=Path(__file__).resolve().parent.parent
    print(relatorio(raiz,json.loads((raiz/'dados'/'processados'/'indicadores.json').read_text(encoding='utf-8'))))
