import {Component, OnInit, ViewChild} from '@angular/core';
import {MatPaginator} from '@angular/material/paginator';
import {MatSort} from '@angular/material/sort';
import {MatTableDataSource} from '@angular/material/table';
import * as d3 from 'd3';

export interface DataHeaders {
  id: number;
  postal: string;
  price: string;
  map: string;
}

@Component({
  selector: 'app',
  styleUrls: ['app.css'],
  templateUrl: 'app.html',
})
export class App implements OnInit {
  displayedColumns: string[] = ['id', 'postal', 'price', 'map'];
  dataSource: MatTableDataSource<DataHeaders>;

  @ViewChild(MatPaginator, {static: true}) paginator: MatPaginator;
  @ViewChild(MatSort, {static: true}) sort: MatSort;

  constructor() {

  }

  async ngOnInit() {      
    var rawData :DataHeaders[] = [];

    await d3.csv('assets/parsed_result.csv')
    .then(function(data) {
      let i = 1;
      data.forEach(function (elem) {
        rawData.push({
          id: i,
          postal: elem['Postal Code'],
          price: parseFloat(elem['Price']).toFixed(2).toString(),
          map: 'Unknown'
        });
        i+=1;
      })
      console.log(rawData)

    })
    .catch(function(error){
       // handle error   
    })
    this.dataSource = new MatTableDataSource(rawData);

    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }
}