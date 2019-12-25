def Ticket_Receipt(receipt_info):
    msg_part_1 = """
	<table border="0" cellpadding="0" cellspacing="0" height="100%" width="100%"><tbody><tr>
	<td align="center" valign="top">
							
							<table border="0" cellpadding="0" cellspacing="0" width="600" id="m_6103953236132574569template_container" style="background-color:#fdfdfd;border:1px solid #dcdcdc;border-radius:3px">
	<tbody><tr>
	<td align="center" valign="top">
										
										<table border="0" cellpadding="0" cellspacing="0" width="600" id="m_6103953236132574569template_header" style="background-color:#000000;color:#ffffff;border-bottom:0;font-weight:bold;line-height:100%;vertical-align:middle;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;border-radius:3px 3px 0 0"><tbody><tr>
	<td id="m_6103953236132574569header_wrapper" style="padding:36px 48px;display:block">
													<h1 style="font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:30px;font-weight:300;line-height:150%;margin:0;text-align:left;color:#ffffff">Thank you for your purchase - Enjoy the Show!</h1>
												</td>
											</tr></tbody></table>

	</td>
								</tr>
	<tr>
	<td align="center" valign="top">
										
										<table border="0" cellpadding="0" cellspacing="0" width="600" id="m_6103953236132574569template_body"><tbody><tr>
	<td valign="top" id="m_6103953236132574569body_content" style="background-color:#fdfdfd">
													
													<table border="0" cellpadding="20" cellspacing="0" width="100%"><tbody><tr>
	<td valign="top" style="padding:48px 48px 0">
																<div id="m_6103953236132574569body_content_inner" style="color:#737373;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:14px;line-height:150%;text-align:left">

	<p style="margin:0 0 16px">Hi {},</p>
	<p style="margin:0 0 16px">Just to let you know — we've received your order, and it is now being processed:</p> 
	<p style="margin:0 0 16px"> Please note that your tickets are attached within this email</p>


	<h2 style="color:#000000;display:block;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:18px;font-weight:bold;line-height:130%;margin:0 0 18px;text-align:left">
		{}</h2>
	""".format(receipt_info[0], receipt_info[1])

    msg_part_2 = """
	<div style="margin-bottom:40px">
		<table class="m_6103953236132574569td" cellspacing="0" cellpadding="6" border="1" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;width:100%;font-family:'Helvetica Neue',Helvetica,Roboto,Arial,sans-serif">
	<thead><tr>
	<th class="m_6103953236132574569td" scope="col" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left">Product</th>
					<th class="m_6103953236132574569td" scope="col" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left">Quantity</th>
					<th class="m_6103953236132574569td" scope="col" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left">Price Per</th>
				</tr></thead>"""

    msg_part_3 = ''
    for key, value in receipt_info[2].items():
        msg_part_2 += '''
	<tbody><tr class="m_6103953236132574569order_item">
	<td class="m_6103953236132574569td" style="color:#737373;border:1px solid #e4e4e4;padding:12px;text-align:left;vertical-align:middle;font-family:'Helvetica Neue',Helvetica,Roboto,Arial,sans-serif;word-wrap:break-word">
			{}	</td>
			<td class="m_6103953236132574569td" style="color:#737373;border:1px solid #e4e4e4;padding:12px;text-align:left;vertical-align:middle;font-family:'Helvetica Neue',Helvetica,Roboto,Arial,sans-serif">
				{}		</td>
			<td class="m_6103953236132574569td" style="color:#737373;border:1px solid #e4e4e4;padding:12px;text-align:left;vertical-align:middle;font-family:'Helvetica Neue',Helvetica,Roboto,Arial,sans-serif">
				<span class="m_6103953236132574569woocommerce-Price-amount m_6103953236132574569amount"><span class="m_6103953236132574569woocommerce-Price-currencySymbol">$</span>{}</span>		</td>
		</tr></tbody>

		'''.format(key, value[0], value[1])

    msg_part_4 = """

	<tfoot>
	<tr>
	<th class="m_6103953236132574569td" scope="row" colspan="2" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left;border-top-width:4px">Subtotal:</th>
							<td class="m_6103953236132574569td" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left;border-top-width:4px"><span class="m_6103953236132574569woocommerce-Price-amount m_6103953236132574569amount"><span class="m_6103953236132574569woocommerce-Price-currencySymbol">$</span>{}</span></td>
						</tr>
	<tr>
	<th class="m_6103953236132574569td" scope="row" colspan="2" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left">Fees:</th>
							<td class="m_6103953236132574569td" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left"><span class="m_6103953236132574569woocommerce-Price-amount m_6103953236132574569amount"><span class="m_6103953236132574569woocommerce-Price-currencySymbol">$</span>{}</span></td>
						</tr>
	<tr>
	<th class="m_6103953236132574569td" scope="row" colspan="2" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left">HST:</th>
							<td class="m_6103953236132574569td" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left"><span class="m_6103953236132574569woocommerce-Price-amount m_6103953236132574569amount"><span class="m_6103953236132574569woocommerce-Price-currencySymbol">$</span>{}</span></td>
						</tr>

	<tr>
	<th class="m_6103953236132574569td" scope="row" colspan="2" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left">Total:</th>
							<td class="m_6103953236132574569td" style="color:#737373;border:1px solid #e4e4e4;vertical-align:middle;padding:12px;text-align:left"><span class="m_6103953236132574569woocommerce-Price-amount m_6103953236132574569amount"><span class="m_6103953236132574569woocommerce-Price-currencySymbol">$</span>{}</span></td>
						</tr>
	</tfoot>
	</table>
	</div>

	
	<table id="m_6103953236132574569addresses" cellspacing="0" cellpadding="0" border="0" style="width:100%;vertical-align:top;margin-bottom:40px;padding:0"><tbody><tr>
	<td valign="top" width="50%" style="text-align:left;font-family:'Helvetica Neue',Helvetica,Roboto,Arial,sans-serif;border:0;padding:0">
				<h2 style="color:#000000;display:block;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:18px;font-weight:bold;line-height:130%;margin:0 0 18px;text-align:left">Billing address</h2>

				<address class="m_6103953236132574569address" style="padding:12px;color:#737373;border:1px solid #e4e4e4">
					{} {}<br>{},<br>{}&nbsp;&nbsp;{}								<br>{}													<br><a href="mailto:{}" target="_blank">{}</a>							</address>
			</td>
				</tr></tbody></table>
	<p style="margin:0 0 16px">
	Thanks!</p>
																</div>
															</td>
														</tr></tbody></table>

	</td>
											</tr></tbody></table>

	</td>
								</tr>
	<tr>
	<td align="center" valign="top">
										
										<table border="0" cellpadding="10" cellspacing="0" width="600" id="m_6103953236132574569template_footer"><tbody><tr>
	<td valign="top" style="padding:0;border-radius:6px">
													<table border="0" cellpadding="10" cellspacing="0" width="100%"><tbody><tr>
	<td colspan="2" valign="middle" id="m_6103953236132574569credit" style="border-radius:6px;border:0;color:#666666;font-family:&quot;Helvetica Neue&quot;,Helvetica,Roboto,Arial,sans-serif;font-size:12px;line-height:125%;text-align:center;padding:0 48px 48px 48px">
																<p><a href="#" target="_blank" data-saferedirecturl="&amp;source=gmail&amp;ust=1564165201717000&amp;usg=AFQjCNGz4gNyL65EiexzNKCbjvZ0sbcuSA">Veronika's Musical Theatre</a> – Event Tickets</p>
															</td>
														</tr></tbody></table>
	</td>
											</tr></tbody></table>

	</td>
								</tr>
	</tbody></table>
	</td>
					</tr></tbody></table>
					""".format(receipt_info[3], receipt_info[4], receipt_info[5], receipt_info[6], receipt_info[7], receipt_info[8], receipt_info[9], receipt_info[10], receipt_info[11], receipt_info[12], receipt_info[13], receipt_info[14])
    total_msg = msg_part_1 + msg_part_2 + msg_part_3 + msg_part_4
    return total_msg
