import ccxt.async_support as ccxt
import ccxt, config, emoji, time, requests, json
from kucoin.client import Market
import hmac
import hashlib
import asyncio
from urllib.parse import urlencode


async def okex():

    okex = ccxt.okx({
        'apiKey': config.okx_api_key,
        'secret': config.okx_secret,
        'password': config.okx_passhrase,
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = okex.fetch_currencies()
    results_exchange = {}
    for currency, dictionary in currencies.items():
        token_info = {}
        for network, info in dictionary['networks'].items():
            token_info[network] = info['info']['canDep'], info['info']['canWd']
        results_exchange[currency] = token_info
        token_info = {}

    return results_exchange


async def binance():

    binance = ccxt.binance({
        'apiKey': config.binance_api_key,
        'secret': config.binance_secret,
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = binance.fetch_currencies()
    results_exchange = {}

    for currency, dictionary in currencies.items():
        token_info = {}
        for i in dictionary['info']['networkList']:
            token_info[i['network']] = i['depositEnable'], i['withdrawEnable']
        results_exchange[currency] = token_info
        token_info = {}

    return results_exchange

# class Signature:
#
#     def __init__(self, api_key: str, secret_key: str):
#         self.__secret_key = secret_key
#         self._headers = {
#             "X-MEXC-APIKEY": api_key,
#             "Content-Type": "application/json"
#         }
#
#     def _get_signed_params(self, params: dict=None) -> dict:
#         if params and 'self' in params:
#             params.pop('self')
#             params = {key:value for key, value in params.items() if value is not None}
#         parameters = params.copy() if params is not None else dict()
#         parameters['recvWindow'] = 60000
#         parameters['timestamp'] = int(time.time()*1000)
#         query_string = urlencode(parameters)
#         parameters['signature'] = hmac.new(self.__secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
#         return urlencode(parameters)
#
# async def mexc():
#
#     api_key = config.mexc_api_key
#     api_secret = config.mexc_secret
#
#     base_url = 'https://api.mexc.com'
#     query_url = '/api/v3/capital/config/getall'
#
#     expires = str(int(time.time()) + 5)
#     signature = Signature(config.mexc_api_key, config.mexc_secret)
#
#     headers = {
#         'Content-Type': 'application/json',
#         'X-MEXC-APIKEY': api_key,
#         'X-MEXC-SIGNATURE': signature,
#         'X-MEXC-TIMESTAMP': expires
#     }
#
#     response = requests.get(base_url + query_url, headers=headers)
#     if response.status_code == 200:
#         data = response.json()
#         # Process the data as needed
#     else:
#         print(f"Request failed with status code: {response.status_code}")
#         print(response.text)


async def huobi():

    huobi = ccxt.huobi()

    currencies = huobi.fetch_currencies()
    results_exchange = {}

    for currency, dictionary in currencies.items():
        token_info = {}
        for i in dictionary['info']['chains']:
            canDep = True if i['depositStatus'] == 'allowed' else False
            canWh = True if i['withdrawStatus'] == 'allowed' else False
            token_info[i['displayName']] = canDep, canWh
        results_exchange[currency] = token_info
        token_info = {}

    return results_exchange


async def gate():

    gate = ccxt.gate({
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = gate.fetch_currencies()
    results_exchange = {}

    for currency, info in currencies.items():
        if '_' in currency:
            if currency.split('_')[0] not in results_exchange:
                results_exchange[currency.split('_')[0]] = {}
            try:
                results_exchange[currency.split('_')[0]][info['info']['chain']] = info['deposit'], info[
                    'withdraw']
            except:
                continue

        else:
            if currency not in results_exchange:
                results_exchange[currency] = {}
            try:
                results_exchange[currency][info['info']['chain']] = info['deposit'], info['withdraw']
            except:
                continue

    return results_exchange


async def bybit():

    bybit = ccxt.bybit({
        'apiKey': config.bybit_api_key,
        'secret': config.bybit_secret,
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = bybit.fetch_currencies()
    results_exchange = {}

    for currency, dictionary in currencies.items():
        token_info = {}
        for network, info in dictionary['networks'].items():
            token_info[network] = info['deposit'], info['withdraw']
        results_exchange[currency] = token_info
        token_info = {}

    return results_exchange


async def ascendex():

    response = requests.get('https://ascendex.com/api/pro/v2/assets').text
    results_exchange = {}
    currencies = json.loads(response)

    for info in currencies['data']:
        token_info = {}
        for network in info['blockChain']:
            token_info[network['chainName']] = network['allowDeposit'], network['allowWithdraw']
        results_exchange[info['assetCode']] = token_info

    return results_exchange


async def kucoin(token):

    response = {}
    chains_info = {}

    market = Market(url='https://api.kucoin.com')
    info = market.get_currency_detail_v2(currency=token)

    for chain in info['chains']:
        chains_info[chain['chainName']] = chain['isDepositEnabled'], chain['isWithdrawEnabled']

    response[token] = chains_info
    return response


async def cryptocom():

    base_url = 'https://api.crypto.com/v2/'

    API_KEY = config.cryptocom_api_key
    SECRET_KEY = config.cryptocom_secret

    req = {
        "id": 14,
        "method": "private/get-currency-networks",
        "api_key": API_KEY,
        "params": {},
        "nonce": int(time.time() * 1000)
    }

    param_str = ""
    MAX_LEVEL = 3

    def params_to_str(obj, level):
        if level >= MAX_LEVEL:
            return str(obj)

        return_str = ""
        for key in sorted(obj):
            return_str += key
            if obj[key] is None:
                return_str += 'null'
            elif isinstance(obj[key], list):
                for subObj in obj[key]:
                    return_str += params_to_str(subObj, ++level)
            else:
                return_str += str(obj[key])
        return return_str

    if "params" in req:
        param_str = params_to_str(req['params'], 0)

    payload_str = req['method'] + str(req['id']) + req['api_key'] + param_str + str(req['nonce'])

    req['sig'] = hmac.new(
        bytes(str(SECRET_KEY), 'utf-8'),
        msg=bytes(payload_str, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    response = requests.post(base_url + 'private/get-currency-networks', json=req,
                             headers={
                                 'Content type': 'application/json'}).text
    result = json.loads(response)['result']['currency_map']
    results_exchange = {}

    for currency, info in result.items():
        token_info = {}
        for network in info['network_list']:
            token_info[network['network_id']] = network['deposit_enabled'], network['withdraw_enabled']
        results_exchange[currency] = token_info

    return results_exchange


async def bitget():

    bitget = ccxt.bitget({
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = bitget.fetch_currencies()
    results_exchange = {}

    for token, info in currencies.items():
        token_info = {}
        for network in info['info']['chains']:
            token_info[network['chain']] = (True, True, float(network['withdrawFee'])) if network[
                                                                                              'withdrawable'] == 'true' else (
            False, False)
        results_exchange[token] = token_info

    return results_exchange


async def lbank():

    url = 'https://api.lbkex.com/v2/withdrawConfigs.do'
    currencies = requests.get(url).json()
    results_exchange = {}

    for data in currencies['data']:
        if data['assetCode'].upper() in results_exchange.keys():
            if 'fee' in data.keys():
                results_exchange[data['assetCode'].upper()][data['chain'].upper()] = (
                    True, True, float(data['fee'])) if data['canWithDraw'] == True else (False, False)
            else:
                results_exchange[data['assetCode'].upper()][data['chain'].upper()] = (
                    True, True) if data['canWithDraw'] == True else (
                    False, False)


        else:
            results_exchange[data['assetCode'].upper()] = {}

            if 'fee' in data and 'chain' in data:
                results_exchange[data['assetCode'].upper()][data['chain'].upper()] = (
                            True, True, float(data['fee'])) if data['canWithDraw'] == True else (
                            False, False)

            elif 'fee' in data.keys():

                results_exchange[data['assetCode'].upper()][data['assetCode'].upper()] = (
                            True, True, float(data['fee'])) if data['canWithDraw'] == True else (
                            False, False)

            elif 'chain' in data.keys():

                results_exchange[data['assetCode'].upper()][data['chain'].upper()] = (
                                True, True) if data['canWithDraw'] == True else (
                                False, False)

    return results_exchange

async def digifinex():

    url = 'https://openapi.digifinex.com/v3/currencies'
    response = requests.get(url).json()
    results_exchange = {}

    for info in response['data']:
        if info['currency'] in results_exchange.keys():
            results_exchange[info['currency']][info['chain']] = bool(info['deposit_status']), bool(info['withdraw_status']), info['min_withdraw_fee']
        else:
            results_exchange[info['currency']] = {}
            results_exchange[info['currency']][info['chain']] = bool(info['deposit_status']), bool(info['withdraw_status']), info['min_withdraw_fee']

    return results_exchange

async def whitebit():

    whitebit = ccxt.whitebit({
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = whitebit.fetch_currencies()
    results_exchange = {}

    for token, data in currencies.items():

        if data['info']['can_withdraw'] == False and data['info']['can_deposit'] == False:

            if 'networks' in data['info'].keys():
                results_exchange[token] = {
                    data['info']['networks']['default']: (False, False)}
            else:
                results_exchange[token] = {'Network': (False, False)}

        elif 'networks' not in data['info'].keys():
            pass

        elif 'deposits' not in data['info']['networks'].keys():

            for chain in data['info']['networks']['withdraws']:
                if token in results_exchange.keys():
                    results_exchange[token][chain] = False, True
                else:
                    results_exchange[token] = {}
                    results_exchange[token][chain] = False, True

        else:
            for chain in data['info']['networks']['deposits']:
                if token in results_exchange.keys():
                    results_exchange[token][chain] = (True, True) if chain in data['info']['networks'][
                        'withdraws'] else (False, False)
                else:
                    results_exchange[token] = {}
                    results_exchange[token][chain] = (True, True) if chain in data['info']['networks'][
                        'withdraws'] else (False, False)

    return results_exchange

async def bitrue():

    bitrue = ccxt.bitrue({
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = bitrue.fetch_currencies()
    results_exchange = {}

    for token, data in currencies.items():
        for chain in data['info']['chainDetail']:
            if token in results_exchange.keys():
                results_exchange[token][chain['chain']] = chain['enableDeposit'], chain['enableWithdraw'], float(chain['withdrawFee'])
            else:
                results_exchange[token] = {}
                results_exchange[token][chain['chain']] = chain['enableDeposit'], chain['enableWithdraw'], float(chain['withdrawFee'])

    return results_exchange

async def xt():

    xt = ccxt.xt({
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = xt.fetch_currencies()
    results_exchange = {}

    for token, data in currencies.items():
        for chain in data['info']['supportChains']:
            if token in results_exchange.keys():
                results_exchange[token][chain['chain']] = chain['depositEnabled'], chain['withdrawEnabled'], float(chain['withdrawFeeAmount'])
            else:
                results_exchange[token] = {}
                results_exchange[token][chain['chain']] = chain['depositEnabled'], chain['withdrawEnabled'], float(chain['withdrawFeeAmount'])

    return results_exchange

async def coinex():

    coinex = ccxt.coinex({
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = coinex.fetch_currencies()
    results_exchange = {}

    for token, data in currencies.items():
        for chain, info in data['networks'].items():
            if token in results_exchange.keys():
                results_exchange[token][chain] = info['info']['can_deposit'], info['info']['can_withdraw'], float(info['info']['withdraw_tx_fee'])
            else:
                results_exchange[token] = {}
                results_exchange[token][chain] = info['info']['can_deposit'], info['info']['can_withdraw'], float(info['info']['withdraw_tx_fee'])

    return results_exchange

async def probit():

    probit = ccxt.probit({
        'enableLimitRate': True,
        'timeout': 30000,
    })

    currencies = probit.fetch_currencies()
    results_exchange = {}

    for token, data in currencies.items():
        for chain, info in data['networks'].items():
            if token in results_exchange.keys():
                results_exchange[token][chain] = info['deposit'], info['withdraw'], float(info['fee'])
            else:
                results_exchange[token] = {}
                results_exchange[token][chain] = info['deposit'], info['withdraw'], float(info['fee'])

    return results_exchange

async def create_response(results, token):

    dictionary = {}
    exchange_info = []
    for exchange in results.keys():
        if token in results[exchange].keys():
            exchange_info = []
            for network, info in results[exchange][token].items():
                exchange_info.append(
                    f'{network}: Deposits {emoji.emojize(":check_mark_button:") if info[0] == True else emoji.emojize(":cross_mark:")}, Withdrawals {emoji.emojize(":check_mark_button:") if info[1] == True else emoji.emojize(":cross_mark:")}\n')
            dictionary[exchange] = exchange_info
            exchange_info = []
        else:
            continue

    response = []
    for exchange, networks in dictionary.items():
        response.append(f'{exchange.strip()}:\n\n{"".join(networks)}')
    return response


last_time_check = time.time()
results = {}


async def check_token(token):
    global last_time_check
    global results

    start_time = time.time()

    results['OKX'] = await okex()
    results['Binance'] = await binance()
    results['Huobi'] = await huobi()
    results['Gate'] = await gate()
    results['Ascendex'] = await ascendex()
    results['Kucoin'] = await kucoin(token)
    results['Cryptocom'] = await cryptocom()
    results['Bybit'] = await bybit()
    results['Bitget'] = await bitget()
    results['Lbank'] = await lbank()
    results['Digifinex'] = await digifinex()
    results['Whitebit'] = await whitebit()
    results['Bitrue'] = await bitrue()
    results['XT'] = await xt()
    results['Coinex'] = await coinex()
    results['Probit'] = await probit()

    # results['MEXC'] = await mexc()

    last_time_check = time.time()
    print(f'The checking took {round(time.time() - start_time, 1)} seconds')
    return await create_response(results, token)


token_info = asyncio.run(check_token('ETH'))
response = '\n\n'.join(token_info)
if response == '':
    print("There isn't a token with this ticker on available exchanges")
else:
    print(response)
