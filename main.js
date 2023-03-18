class BaseTableView{


	addToTable(cmd) {
		this.iter += 1;
		cmd["num"] = this.iter;

		// cmd[0] = this.iter;
		

		// <th> ${this.iter} </th>
		// 	<td> ${cmd["lat"]} </td>
		// 	<td> ${cmd["lon"]} </td>
		// 	<td> ${cmd["hgt"]} </td>
		// 	<td> ${cmd["utc"]} </td>



		this.t_body.prepend(`
		<tr>

			${this.rows.reduce((acc, curr) => {
				return acc + `<td>${cmd[curr]}</td>`
			}, '')}

		</tr>
		`);
	}

	createTable(id_wrapp, rows) {
		$("#" + id_wrapp).append(`
		<div class="panel-body table-responsive">

			<table id="${id_wrapp}_table" class="table table-bordered table-striped">
			  <thead>
				<tr>
					${rows.reduce((acc, curr) => {
						return acc + `<th scope="col">${curr}</th>`
					}, '')}
				</tr>

		
				
			  </thead>
				<tbody class="overflow-scroll">
				</tbody>

			</table>
		</div>
		<button id="${id_wrapp}_clear">Clear</button>

		`
		);
		this.rows = rows;
		this.t_body = $('#' + id_wrapp + '_table' + ' tbody');
		this.clear_btn = $("#" + id_wrapp + "_" + "clear");
		this.clear_btn.click((el) => {
			this.clearTable();
		});		
		


	}	


	constructor(id_wrapp, rows) {
		this.received = null;
		this.iter = 0;
		this.t_body = null;
		this.clear_btn = null;
		this.createTable(id_wrapp, rows);
	}


	clearTable() {
		if (this.clear_btn != null) {
			this.t_body.text("");
		}
	}

}

class MarktimeTableView extends BaseTableView{
		addToTable(cmd) {
			this.iter += 1;
			this.t_body.prepend(`
			<tr>
				<th> ${this.iter} </th>
				<td> ${cmd["lat"]} </td>
				<td> ${cmd["lon"]} </td>
				<td> ${cmd["hgt"]} </td>
				<td> ${cmd["utc"]} </td>


			</tr>
			`);
		}

		createTable(id_wrapp, rows) {
			console.log("create table gpgga");
			$("#" + id_wrapp).append(`
			<div class="panel-body table-responsive">

				<table id="${id_wrapp}_table" class="table table-bordered table-striped">
				  <thead>
					<tr>
						${rows.reduce((acc, curr) => {
							return acc + `<th scope="col">${curr}</th>`
						}, '')}
					</tr>
	
			
					
				  </thead>
					<tbody class="overflow-scroll">
					</tbody>
	
				</table>
			</div>
			<button id="${id_wrapp}_clear">Clear</button>

			`
			);

			this.t_body = $('#' + id_wrapp + '_table' + ' tbody');
			this.clear_btn = $("#" + id_wrapp + "_" + "clear");
			this.clear_btn.click((el) => {
				this.clearTable();
			});		
			


		}	
	
	constructor(id_wrapp, rows) {
		super();
		this.createTable(id_wrapp, rows)
		
		
	}


}

class MarkposTableView extends BaseTableView{
	createTable() {
		console.log("create_markpos_tableview");
	
	}
	constructor() {
		super();
		this.received = $("#received_markpos");
		
	}


}
class GpggaTableView extends BaseTableView {
	createTable() {
		console.log("create table gpgga");
		this.gpgga_table_wrapp.append(`
			<table id="gpgga_table" class="table table-bordered table-striped">
			  <thead>
				<tr>
				  <th scope="col">num</th>
				  <th scope="col">utc</th>
				  <th scope="col">lat</th>
				  <th scope="col">lon</th>
				  <th scope="col">GPS_qual</th>
				  <th scope="col">sats</th>

		
				</tr>
			  </thead>
				  <tbody class="overflow-scroll">
				</tbody>

			</table>`
		)
		
	}

	constructor() {
		super();
		this.gpgga_table_wrapp = $('#gpgga_table_wrapp');
		this.createTable();
		this.gpgga_table_body = $('#gpgga_table tbody');

	}

	addToTable = (cmd) => {
		
		this.iter += 1
		// "type": "ascii", "name": "$GPGGA"
		if (cmd["type"] == "ascii" && cmd["name"] == "$GPGGA") {
			this.gpgga_table_body.append(`
			<tr>
				<th> ${this.iter} </th>
				<td> ${cmd["utc"].slice(0, 2) + ":" + cmd["utc"].slice(2, 4) + ":" + cmd["utc"].slice(4, 6)}</td>
				<td> ${cmd["lat"]} </td>
				<td> ${cmd["lon"]} </td>
				<td> ${cmd["GPS qual"]} </td>
				<td> ${cmd["sats"]} </td>

			</tr>
			`);
		}

	}


}


class TrashView extends BaseTableView{
	createTable() {
		console.log("create_trasg");
	
	}
	constructor() {
		super();
		
		this.received = $("#received_rangecmp");
		
		
	}



	addToTable(cmd){
		this.iter += 1;
		this.received.append(JSON.stringify(cmd));
		this.received.append($('<br/>'));
	}

}







class ManagerViews{


	activePage(cmd) {
		this.quick_info.removeClass(this.alertFalse);
		this.quick_info.addClass(this.alertOk);

		var text_msg = "msg" in cmd ? cmd["msg"] : "COM порт инициализирован, Ожидание данных...";
		this.quick_info.text(cmd["msg"])
		this.page.show();
		this.quick_info.text(text_msg);
		this.initComPORT = true;
	}

	parseCmd({data : cmd}) {
		cmd = JSON.parse(cmd);
		if (cmd["type"] = "err" && cmd["name"] == "init_err") {
			this.quick_info.removeClass(this.alertOk);
			this.quick_info.addClass(this.alertFalse);
			this.quick_info.text(cmd["msg"]);
			this.page.hide("slow");

		} else {
			if (!this.initComPORT) {
				this.activePage(cmd);
			} 

		}


		// else if (cmd["ok"] = "err" && cmd["name"] == "init_ok") {
			
		// }
		



	}
	
	addToTable({data : cmd}) {
		
		console.log(cmd);
		cmd = JSON.parse(cmd);
		if (cmd["name"] == "RANGECMP") {
			this.trash_view.addToTable(cmd);
		}
		else if (cmd["name"] == "$GPGGA") {
			cmd["utc"] = cmd["utc"].slice(0, 2) + ":" + cmd["utc"].slice(2, 4) + ":" + cmd["utc"].slice(4, 6);
			this.gpgga_view.addToTable(cmd);	
				$("#quick_info").text(`Время: ${cmd["utc"]}, Связь : ${cmd["GPS qual"]}, Спутники : ${cmd["sats"]}, Кол-во сделанных меток : ${cmd["total_marks"]}`);
		}
		// else if ((cmd["name"] == "MARKPOS")) {
		// 	this.marktime_view.addToTable(cmd);
		// }
		else if ((cmd["name"] == "FULL_CMD")) {
			this.marktime_view.addToTable(cmd);

		}
		

	}
	constructor(){
		// this.gpgga_view    = new GpggaTableView();
		this.initComPORT = false;
		this.page = $("#wrapp_com_port_info");
		this.alertOk = "alert-success";
		this.alertFalse = "alert-warning";
		this.quick_info = $("#quick_info");
		this.trash_view    = new TrashView();
		this.marktime_view = new BaseTableView("marktime", ["num", "lat", "lon", "hgt", "utc"]);
		this.gpgga_view = new BaseTableView("gpgga", ["num", "utc", "lat", "lon", "GPS qual", "sats"]);

		// this.markpos_view  = new MarkposTableView();

	}
}

$(document).ready(function () {




	// var table = $('#gpgga_table tbody');

	

	var socket = new WebSocket("ws://localhost:8080/ws");
	global_view = new ManagerViews();
	socket.onopen = function () {
		// global_view = new ManagerViews();

		console.log("connected");
		
	};

	socket.onmessage = function (message) {
		global_view.addToTable(message);
		global_view.parseCmd(message);
	};

	socket.onclose = function () {
		console.log("disconnected");
	};

	var sendMessage = function (message) {
		console.log("sending:" + message.data);
		socket.send(message.data);
	};


	// GUI Stuff


	// send a command to the serial port
	$("#cmd_send").click(function (ev) {
		ev.preventDefault();
		var cmd = $('#cmd_value').val();
		sendMessage({ 'data': cmd });
		$('#cmd_value').val("");
	});

	$('#clear').click(function () {
		received.empty();
	});


});
