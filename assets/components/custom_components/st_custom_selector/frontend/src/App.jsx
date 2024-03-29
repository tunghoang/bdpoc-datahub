import { useEffect, useState } from "react";
import {
	Streamlit,
	withStreamlitConnection,
	ArrowTable,
} from "streamlit-component-lib";
import { Button, Checkbox, Row, Col, Typography } from "antd";
import { Table, Int } from "apache-arrow";
import "./App.css";

const FilterOptions = ({ onChange, labels, options, span }) => {
	return (
		<Checkbox.Group onChange={onChange}>
			<Row gutter={[16, 16]}>
				{options.map((option, index) => {
					return (
						<Col span={span} key={index}>
							<Checkbox value={option}>{labels[index]}</Checkbox>
						</Col>
					);
				})}
			</Row>
		</Checkbox.Group>
	);
};

const filterTable = (table, condition) => {
	const filteredData = {};

	for (const column of table.schema.fields) {
		const columnName = column.name;
		const columnData = [];

		for (let i = 0; i < table.length; i++) {
			if (condition(table, i)) {
				columnData.push(table.getColumn(columnName).get(i));
			}
		}

		const columnVector = table.getColumn(columnName);
		const VectorType = columnVector.constructor;
		filteredData[columnName] = VectorType.from({
			values: columnData,
			type: columnVector.type,
		});
	}

	return Table.new(filteredData);
};

function toIsoString(date) {
  let tzo = 7,
      dif = tzo >= 0 ? '+' : '-',
      pad = function(num) {
          return (num < 10 ? '0' : '') + num;
      };

  return date.getFullYear() +
      '-' + pad(date.getMonth() + 1) +
      '-' + pad(date.getDate()) +
      'T' + pad(date.getHours()) +
      ':' + pad(date.getMinutes()) +
      ':' + pad(date.getSeconds()) +
      dif + pad(Math.floor(Math.abs(tzo) / 60)) +
      ':' + pad(Math.abs(tzo) % 60);
}

function App({ args }) {
	useEffect(() => {
		Streamlit.setFrameHeight();
	});
	const [tags, setTags] = useState([]);
	const [alertTime, setAlertTime] = useState([]);
	const handleApply = () => {
		const _table = filterTable(data.table, (table, rowIndex) => {
			return (
				tags.includes(table.getColumnAt(2).get(rowIndex)) &&
				alertTime.includes(table.getColumnAt(0).get(rowIndex))
			);
		});
		const indexTable = Table.new({
			index: data.table.getColumnAt(0).constructor.from({
				values: Array.from({ length: _table.length }, (_, i) => i),
				type: new Int(true, 64),
			}),
		});
		// const columnTable = Table.new({
		// 	columns: data.columnsTable.getColumnAt(0).constructor.from({
		// 		values: data.columnsTable
		// 			.toArray()
		// 			.map((row) => row[0])
		// 			.slice(1),
		// 		type: data.columnsTable.getColumnAt(0).type,
		// 	}),
		// });
		const arrT = new ArrowTable(
			_table.serialize(),
			indexTable.serialize(),
			data.columnsTable.serialize()
		);
		Streamlit.setComponentValue(arrT);
	};
	const { data } = args;
	const tagOptions = [...new Set(data.table.getColumnAt(2))];

	let timeArray = [...data.table.getColumnAt(0)];
	let typeArray = [...data.table.getColumnAt(3)];
	let combinedArray = timeArray.map(
		(item, idx) => `${toIsoString(new Date(item))} (${typeArray[idx]})`
	);
	const stopStartEventList = [...new Set(combinedArray)];
	const alertTimeOptions = [...new Set(timeArray)];
	const handleSelectTags = (selectedTags) => {
		setTags(selectedTags);
	};
	const handleSelectAlertType = (selectedAlertType) => {
		setAlertTime(selectedAlertType);
	};

	return (
		<Row gutter={[16, 16]}>
			<Col xs={24}>
				<Typography.Title level={5}>Tags:</Typography.Title>
				<FilterOptions
					onChange={handleSelectTags}
					labels={tagOptions}
					options={tagOptions}
					span={6}
				/>
			</Col>
			<Col xs={24}>
				<Typography.Title level={5}>Events:</Typography.Title>
				<FilterOptions
					onChange={handleSelectAlertType}
					labels={stopStartEventList}
					options={alertTimeOptions}
					span={12}
				/>
			</Col>
			<Col xs={24}>
				<Button onClick={handleApply}>Apply</Button>
			</Col>
		</Row>
	);
}

export default withStreamlitConnection(App);
