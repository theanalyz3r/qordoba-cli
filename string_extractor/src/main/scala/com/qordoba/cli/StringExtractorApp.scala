package com.qordoba.cli

import com.opencsv.CSVWriter
import com.qordoba.cli.grammar.StringExtractorLexer
import com.typesafe.scalalogging.slf4j.LazyLogging
import java.io.{BufferedWriter, File, FileWriter, StringWriter}
import org.antlr.v4.runtime.{CharStream, CharStreams, CommonTokenStream, Token}
import scala.collection.JavaConversions._
import scala.collection.mutable.ListBuffer

/**
  * Application that uses a precompiled ANTLR grammar to extract string literals from a given file
  */
object StringExtractorApp extends App with LazyLogging {
  /**
    * Main entry point for the StringExtractor application
    *
    * @param args
    */
  override def main(args: Array[String]) {

    val argMissingText = "Infile and outfile arguments required"
    val usageText = "Usage: StringExtractorApp <infile> <outfile>"

    // TODO: Add support for -f, -d, -o
    val infileName = if (args.size > 0) {
      args.head
    } else {
      println(argMissingText)
      println(usageText)
      return
    }

    val outfileName = if (args.size > 1) {
      args(1)
    } else {
      println(argMissingText)
      println(usageText)
      return
    }

    new StringExtractorApp(infileName, outfileName).extractStrings()

  }
}

class StringExtractorApp(infileName: String, outfileName: String) extends LazyLogging {

  /**
    * Main driver for the class. Calls all relevant methods to extract string literals
    * and write them to the given output file in CSV format.
    */
  def extractStrings() = {
    try {
      // Kick off the lexer
      val tokens: Iterator[Token] = this.getTokens()

      // Inspect each token for something interesting
      val stringLiterals: List[StringLiteral] = this.findStringLiterals(tokens)

      // Send our treasures to a file
      this.generateCsv(stringLiterals, outfileName)

    } catch {
      case e: Exception => {
        logger.error(s"Unable to parse ${infileName}: ${e}")
        throw e
      }
    }
  }

  /**
    * Performs lexical analysis (tokenization) using ANTLR4-generated classes.
    * The underlying grammar is designed to differentiate string literals from
    * all other characters.
    *
    * @return iterator of tokens
    */
  def getTokens(): Iterator[Token] = {
    try {
      val input: CharStream = CharStreams.fromFileName(infileName)
      val lexer: StringExtractorLexer = new StringExtractorLexer(input)
      val tokenStream: CommonTokenStream = new CommonTokenStream(lexer)

      // Activate the lexer
      tokenStream.fill()

      // Retrieve the token iterator
      tokenStream.getTokens().iterator()
    } catch {
      case e: Exception => {
        logger.error(s"Unable to generate tokens for ${infileName}: ${e}")
        throw e
      }
    }
  }

  /**
    * Extracts relevant tokens (i.e. StringLiterals) from a list of arbitrary tokens.
    * Stores related information about where the token was found.
    *
    * @param tokens
    * @return list of StringLiterals
    */
  def findStringLiterals(tokens: Iterator[Token]): List[StringLiteral] = {
    // A place to store everything that should go in the output file
    val allStringLiterals: ListBuffer[StringLiteral] = scala.collection.mutable.ListBuffer.empty[StringLiteral]

    try {
      // Inspect each token for something interesting
      while (tokens.hasNext()) {
        val token: Token = tokens.next()

        // Look for StringLiteral (value of 1 in StringExtractorLexer.tokens)
        if (token.getType() == 1) {
          val stringLiteral: StringLiteral = new StringLiteral(
            filename = infileName,
            text = token.getText(),
            startLineNumber = token.getLine(),
            startCharIdx = token.getCharPositionInLine(),
            endLineNumber = token.getLine(),
            endCharIdx = token.getCharPositionInLine() + token.getText().size - 1  // 0-based index, inclusive
          )
          allStringLiterals += stringLiteral
        }
      }
    } catch {
      case e: Exception => {
        logger.error(s"Unable to filter tokens for ${infileName}: ${e}")
        throw e
      }
    }

    allStringLiterals.toList
  }

  /**
    * Generates a CSV file containing a single record for each given StringLiteral.
    * Generated file is default CSV format (comma-delimited with double quotes for string literals).
    *
    * @param stringLiterals
    * @param outfileName
    */
  def generateCsv(stringLiterals: List[StringLiteral], outfileName: String) = {
    val writer = new StringWriter()
    val csvWriter = new CSVWriter(writer)

    // Convert to a format that OpenCSV can do something with
    val toWrite: List[Array[String]] = stringLiterals.map(stringLiteral => stringLiteral.toStringArray())

    csvWriter.writeAll(toWrite, false)
    csvWriter.close()

    val outfile = new File(outfileName)
    val bw = new BufferedWriter(new FileWriter(outfile))
    bw.write(writer.toString())
    bw.close()

    logger.debug(s"String literals written to ${outfileName}")
  }

}

