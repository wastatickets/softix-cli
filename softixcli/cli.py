import os
import json

import click
import softix

from .validations import validate_fee, validate_token_file

def file_exists(context, param, value):
    if not value:
        return

    filename = value.name
    if os.path.exists(filename):
        raise click.BadParameter('{0} already exists'.format(filename))
    else:
        return value


@click.group()
@click.option('--client-id', help='Client ID', envvar='SOFTIX_CLIENT_ID')
@click.option('--secret', help='Secret', envvar='SOFTIX_SECRET')
@click.option('--seller-code', help='Seller code', envvar='SOFTIX_SELLER_CODE')
@click.pass_context
def cli(context, client_id, secret, seller_code):
    context.obj = {}
    context.obj['client_id'] = client_id
    context.obj['secret'] = secret
    context.obj['seller_code'] = seller_code
    context.obj['softix_client'] = softix.SoftixCore()


@cli.command(name='create-customer')
@click.option("--data", "-d", help="Customer data as json", required=True)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def create_customer(context, data, token):
    """
    Create a new customer.
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        customer_data = json.loads(data)
        customer = softix_client.create_customer(seller_code, **customer_data)
        output = json.dumps(customer)
        click.echo(output)
    except ValueError:
        click.echo("Unable to parse customer data as JSON")
        context.exit(1)
    except softix.exceptions.SoftixError as error:
        context.fail(error.message)

@cli.command(name='add-offer')
@click.argument('basket-id', type=str)
@click.argument('performance-code', type=str)
@click.option('--section', type=str, required=True)
@click.option('--demand', nargs=3, required=True, multiple=True, help='Price Type Code, Quantity, Admits')
@click.option('--fee', required=True, nargs=2, multiple=True, help='Fee: type, code', callback=validate_fee)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def add_offer(context, basket_id, performance_code, section, demand, fee, token):
    """
    Add an offer to an existing basket.
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    demands = [softix.Demand(*d) for d in demand]
    fees = [softix.Fee(*f) for f in fee]
    basket = softix_client.add_offer(seller_code, basket_id, performance_code, section, demands, fees)
    click.echo(json.dumps(basket))


@cli.command(name='create-basket')
@click.argument('performance-code', type=str)
@click.option('--section', type=str, required=True)
@click.option('--demand', nargs=3, required=True, multiple=True, help='Price Type Code, Quantity, Admits')
@click.option('--fee', required=True, nargs=2, multiple=True, help='Fee: type, code', callback=validate_fee)
@click.option('--customer-id', 'customer_id', help='Customer ID', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def create_basket(context, performance_code, section, demand, fee, customer_id, token):
    """
    Create a cart/basket.
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    demands = [softix.Demand(*d) for d in demand]
    fees = [softix.Fee(*f) for f in fee]
    basket = softix_client.create_basket(seller_code, performance_code, section, demands, fees, customer_id=customer_id)
    click.echo(json.dumps(basket))


@cli.command('create-token')
@click.option('--file', 'dest', help='Output destination file', required=False, type=click.File('wb'), callback=file_exists)
@click.pass_context
def create_token(context, dest):
    """
    Create authentication token.
    """
    softix_client = context.obj['softix_client']
    client_id = context.obj['client_id']
    secret = context.obj['secret']
    try:
        auth_data = softix_client.authenticate(client_id, secret)
        if dest:
            dest.write(json.dumps(auth_data))
        else:
            click.echo(json.dumps(auth_data, indent=4))
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)


@cli.command(name='delete-customer')
def delete_customer(context):
    """Delete a customer."""
    pass

@cli.command(name='get-performance-availabilities')
@click.argument('performance-code', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def get_performance_availabilities(context, performance_code, token):
    """
    Get performance availabilities.

    Performance availabilities is basically event information
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        performance_data = softix_client.performance_availabilities(seller_code, performance_code)
        output = json.dumps(performance_data)
        click.echo(output)
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)

@cli.command(name='get-performance-prices')
@click.argument('performance-code', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def get_performance_prices(context, performance_code, token):
    """
    Get performance prices.
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        performance_prices = softix_client.performance_prices(seller_code, performance_code)
        output = json.dumps(performance_prices)
        click.echo(output)
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)

@cli.command(name='get-basket')
@click.argument('basket-id', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def get_basket(context, basket_id, token):
    """
    Get basket.
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        basket = softix_client.basket(seller_code, basket_id)
        output = json.dumps(basket)
        click.echo(output)
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)

@cli.command(name='get-customer')
@click.argument('customer-id', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def get_basket(context, customer_id, token):
    """
    View order details.
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        order = softix_client.customer(seller_code, customer_id)
        output = json.dumps(order)
        click.echo(output)
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)


@cli.command(name='get-order')
@click.argument('order-id', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def get_basket(context, order_id, token):
    """
    View order details.
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        order = softix_client.order(seller_code, order_id)
        output = json.dumps(order)
        click.echo(output)
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)


@cli.command(name='purchase-basket')
@click.argument('basket-id', type=str)
@click.option('--customer-id', 'customer_id', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def purchase_basket(context, basket_id, customer_id, token):
    """
    Purchase basket.

    Returns the order
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        basket = softix_client.purchase_basket(seller_code, basket_id, customer_id)
        output = json.dumps(basket)
        click.echo(output)
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)


@cli.command(name='reverse-order')
@click.argument('order-id', type=str)
@click.option('--token-json', 'token', help='Token JSON', required=True, callback=validate_token_file)
@click.pass_context
def reverse_order(context, order_id, token):
    """
    Reverse the order
    """
    softix_client = context.obj['softix_client']
    seller_code = context.obj['seller_code']
    try:
        refund = softix_client.reverse_order(seller_code, order_id)
        click.echo(refund)
    except softix.exceptions.SoftixError as error:
        click.echo(error.message)
        context.exit(1)


if __name__ == "__main__":
    cli()
